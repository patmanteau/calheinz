import logging
from collections import deque
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from time import sleep

import apprise
import arrow
from tomlkit import parse

log = logging.getLogger("rich")


@dataclass
class Watch:
    path: Path
    url: str
    interval: int  # minutes
    apr: apprise.Apprise

    @property
    def config_file(self) -> Path:
        return self.path / "config.toml"

    @property
    def last_update(self) -> Path:
        return self.path / "last_update.ics"

    @last_update.setter
    def last_update(self, content):
        log.info(f"Updating {self.last_update}")
        with open(self.last_update, "wb") as f:
            f.write(content)

    @classmethod
    def from_path(cls, path: Path) -> "Watch":
        with open(path / "config.toml") as f:
            config = parse(f.read())
        url = config.get("url", str)
        interval = config.get("interval", int)
        notify_url = config.get("notify", str)
        apr = apprise.Apprise()
        apr.add(notify_url)
        return cls(path, url, interval, apr)


def read_watches(path: Path) -> list[Watch]:
    return [Watch.from_path(x) for x in path.iterdir() if x.is_dir()]


def pollqueue(watches: list[Watch]) -> Generator:
    q = deque([(arrow.utcnow(), w) for w in watches])
    while len(q) > 0:
        (next_run, w) = q.popleft()
        now = arrow.utcnow()
        if next_run > now:
            sleep((next_run - now).total_seconds())
        q.append((arrow.utcnow().shift(minutes=w.interval), w))
        log.info(f"Polling {w} now")
        yield w
