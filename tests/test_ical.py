import pytest
from arrow import Arrow

from ical import Event, EventList


def test_ended():
    """
    Test that it correctly checks if Events have ended.
    """
    now = Arrow.now()

    event = Event(
        uid="1234",
        tstamp=now,
        summary="Just a test",
        location="here",
        start=now.shift(minutes=-10),
        end=now.shift(minutes=-5),
    )
    assert event.ended()

    event = Event(
        uid="1234",
        tstamp=now,
        summary="Just a test",
        location="here",
        start=now.shift(minutes=5),
        end=now.shift(minutes=10),
    )
    assert not event.ended()


def test_from_file(calfile_a):
    """
    Test that it parses iCal files.
    """
    assert len(calfile_a.events) == 51


@pytest.fixture
def calfile_a() -> EventList:
    return EventList.from_file(
        "tests/integration/fixtures/campus-termine-2022-10-31.ics"
    )
