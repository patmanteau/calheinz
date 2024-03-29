import logging
import pathlib
import re

import click
from rich.logging import RichHandler

from ical import EventDiff, EventList, compare, format_diffs
from state import pollqueue, read_watches

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
log = logging.getLogger("rich")


def is_url(cnd: str) -> bool:
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # noqa: E501; domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, cnd) is not None


@click.command()
@click.argument("address")
def read(address: str) -> EventList | None:
    return (
        EventList.from_url(address) if is_url(address) else EventList.from_file(address)
    )


@click.command()
@click.argument("lhs")
@click.argument("rhs")
def diff(lhs: str, rhs: str) -> list[EventDiff]:
    lhs_events = EventList.from_url(lhs) if is_url(lhs) else EventList.from_file(lhs)
    rhs_events = EventList.from_url(rhs) if is_url(rhs) else EventList.from_file(rhs)

    diff_events = compare(lhs_events, rhs_events)
    print(format_diffs(diff_events))
    return diff_events


@click.command()
@click.option("--dry-run", is_flag=True, help="Only check for changes, don't update")
@click.argument(
    "dir", type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path)
)
def poll(dir: pathlib.Path, dry_run: bool):
    watches = read_watches(dir)
    for w in watches:
        log.info(f"Polling {w.url} every {w.interval} minutes. Config dir is {w.path}")
    for w in pollqueue(watches):
        known_events = EventList.from_file(w.last_update)
        new_events = EventList.from_url(w.url)
        diff_events = compare(known_events, new_events)
        if len(diff_events) > 0:
            log.debug(f"Found calendar changes: {diff_events}")
            w.apr.notify(body=format_diffs(diff_events))
            print(format_diffs(diff_events))
            if not dry_run:
                w.last_update = new_events.raw


@click.group()
def cli():
    pass


cli.add_command(read)
cli.add_command(diff)
cli.add_command(poll)

if __name__ == "__main__":
    cli()
