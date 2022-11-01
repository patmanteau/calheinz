from dataclasses import dataclass
from typing import Iterable
from uuid import UUID, uuid4
from pathlib import Path
from tomlkit import parse
from collections import deque
from typing import Generator
import arrow
from time import sleep
import apprise

@dataclass
class Watch:
    path: Path
    url: str
    interval: int # minutes
    apr: apprise.Apprise

    @property    
    def config_file(self) -> Path:
        return self.path / 'config.toml'

    @property
    def last_update(self) -> Path:
        return self.path / 'last_update.ics'

    @last_update.setter
    def last_update(self, content):
        with open(self.last_update, 'wb') as f:
            f.write(content)

    @classmethod
    def from_path(cls, path: Path) -> 'Watch':
        with open(path / 'config.toml', 'r') as f:
            config = parse(f.read())
        apr = apprise.Apprise()
        apr.add(config.get('notify', str))
        return cls(path, config.get('url', str), config.get('interval', int), apr)

def read_watches(path: Path) -> list[Watch]:
    return [Watch.from_path(x) for x in path.iterdir() if x.is_dir()]

def pollqueue(watches: list[Watch]) -> Generator:
    q = deque([(arrow.utcnow(), w) for w in watches])
    while len(q) > 0:
        (next_run, w) = q.popleft()
        now = arrow.utcnow()
        if next_run > now:
            sleep((next_run - now).total_seconds())

        print(now)
        q.append((arrow.utcnow().shift(minutes=w.interval), w))
        yield w
        

