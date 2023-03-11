import pytest
from arrow import Arrow

from ical import Event, EventList, compare


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


def test_from_file(calfile_large):
    """
    Test that it parses iCal files.
    """
    assert len(calfile_large.events) == 51


def test_diff(calfile_before, calfile_after):
    """
    Test that it captures differences between iCal files
    """
    diffs = compare(calfile_before, calfile_after)
    assert (len(diffs)) == 6


@pytest.fixture
def calfile_large() -> EventList:
    return EventList.from_file(
        "tests/integration/fixtures/campus-termine-2022-10-31.ics"
    )


@pytest.fixture
def calfile_before() -> EventList:
    return EventList.from_file("tests/integration/fixtures/before.ics")


@pytest.fixture
def calfile_after() -> EventList:
    return EventList.from_file("tests/integration/fixtures/after.ics")
