import click
import re
import difflib
from dataclasses import dataclass, field
import icalendar as ical
import requests as req
from arrow import Arrow
import pathlib
from io import StringIO
from state import Watch, read_watches, pollqueue
import apprise

from ical import Event, EventList, EventDiff, compare

def is_url(cnd: str) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, cnd) is not None


@click.command()
@click.argument('address')
def read(address: str) -> EventList | None:
    return EventList.from_url(address) if is_url(address) else EventList.from_file(address)


def format_difflist(difflist: list[EventDiff]) -> str:
    return ''.join([e.formatted() for e in difflist])

@click.command()
@click.argument('lhs')
@click.argument('rhs')
def diff(lhs: str, rhs: str) -> list[EventDiff]:
    lhs_events = EventList.from_url(lhs) if is_url(lhs) else EventList.from_file(lhs)
    rhs_events = EventList.from_url(rhs) if is_url(rhs) else EventList.from_file(rhs)
    
    diff_events = compare(lhs_events, rhs_events)
    print(format_difflist(diff_events))
    return diff_events


@click.command()
@click.option('--dry-run', is_flag=True, help="Only check for changes, don't update")
@click.argument('dir',type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
def poll(dir: pathlib.Path, dry_run: bool):
    watches = read_watches(dir)
    for w in pollqueue(watches):
        known_events = EventList.from_file(w.last_update)
        new_events = EventList.from_url(w.url)
        diff_events = compare(known_events, new_events)
        if len(diff_events) > 0:
            w.apr.notify(body=format_difflist(diff_events))
            print(format_difflist(diff_events))
            if not dry_run:
                w.last_update = new_events.raw
            

@click.group()
def cli():
    pass

cli.add_command(read)
cli.add_command(diff)
cli.add_command(poll)

if __name__ == '__main__':
    cli()


