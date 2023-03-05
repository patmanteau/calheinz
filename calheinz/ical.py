from dataclasses import dataclass, field
import icalendar as ical
from arrow import Arrow
import requests

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader('calheinz/templates'),
    autoescape=select_autoescape()
)

def datetime_format(value, format='ddd, DD.MM.YYYY HH:mm ZZZ') -> str:
    return value.to('Europe/Berlin').format(format, locale='de-de')

env.filters['dtform'] = datetime_format

@dataclass(frozen=True)
class Event:
    uid: str
    # tstamp changes with each request, so
    # exclude it from equivalence
    tstamp: Arrow = field(compare=False)
    summary: str | None
    location: str | None
    start: Arrow | None
    end: Arrow | None

    @classmethod
    def from_vevent(cls, vevent: ical.Event) -> 'Event':
        summary = vevent.decoded('summary').decode('utf8') if vevent.get('summary') else None
        location = vevent.decoded('location').decode('utf8') if vevent.get('location') else None
        start = Arrow.fromdatetime(vevent.decoded('dtstart')) if vevent.get('dtstart') else None
        end = Arrow.fromdatetime(vevent.decoded('dtend')) if vevent.get('dtend') else None
        return cls(
            uid=vevent.decoded('uid').decode('utf8'),
            tstamp=Arrow.fromdatetime(vevent.decoded('dtstamp')),
            summary=summary,
            location=location,
            start=start,
            end=end,
        )

    def formatted(self: 'Event') -> str:
        return f"""uid: {self.uid}
summary: {self.summary}
location: {self.location}
start: {self.start}
end: {self.end}"""


@dataclass(frozen=True)
class EventList:
    events: list[Event]
    raw: bytes

    @classmethod
    def from_bytes(cls, b) -> 'EventList':
        ecal = ical.Calendar.from_ical(b)
        return cls([Event.from_vevent(x) for x in ecal.walk() if x.name == "VEVENT"], b)

    @classmethod
    def from_url(cls, url: str) -> 'EventList':
        try:
            response = requests.get(url)
            return cls.from_bytes(response.content)
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    
    @classmethod
    def from_file(cls, path: str) -> 'EventList':
        with open(path, 'rb') as f:
            cal = f.read()
        return cls.from_bytes(cal)

@dataclass(frozen=True)
class EventDiff:
    lhs: Event | None
    rhs: Event | None

    def formatted(self) -> str:
        match (self.lhs, self.rhs):
            case (None, e) if isinstance(e, Event):
                template = env.get_template('new.jinja2')
                return template.render(e=e)
            case (e, None) if isinstance(e, Event):
                template = env.get_template('canceled.jinja2')
                return template.render(e=e)
            case (old, new) if isinstance(old, Event) and isinstance(new, Event):
                template = env.get_template('changed.jinja2')
                return template.render(old=old, new=new)
            case _:
                return ''

def compare(lhs: EventList, rhs: EventList) -> list[EventDiff]:
    # see https://stackoverflow.com/a/38240169
    diffs = set(lhs.events) ^ set(rhs.events)
    if len(diffs) < 1:
        # no changes
        return [] 
    diff_uids = {e.uid for e in diffs}
    
    # identify added and removed events by uid set difference
    lhs_uids = {e.uid for e in lhs.events}
    rhs_uids = {e.uid for e in rhs.events}
    added_uids = rhs_uids - lhs_uids
    removed_uids = lhs_uids - rhs_uids

    # if an event is different, but has neither
    # been added or removed, it must have changed
    changed_uids = diff_uids - (added_uids | removed_uids)
    
    # lookup tables to build (old, new) tuples
    lhs_dict = {e.uid: e for e in lhs.events}
    rhs_dict = {e.uid: e for e in rhs.events}
    added_events = [EventDiff(None, rhs_dict[u]) for u in added_uids]
    removed_events = [EventDiff(lhs_dict[u], None) for u in removed_uids]
    changed_events = [EventDiff(lhs_dict[u], rhs_dict[u]) for u in changed_uids]
    
    # roll them into one list
    return [*added_events, *removed_events, *changed_events]
