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

    # all events
    assert (len(diffs)) == 6

    # no expired events:
    # Feature Request Prokrastibot:
    # "Termin entfällt" > 5 Monate her nicht mehr notifizieren. Oder
    # nach 6m-1 Tag aus der eigenen Datenhaltung löschen. Sieht so aus
    # als würde alles was 6 Monate alt ist aus dem Kalender entfernt
    # werden, siehe notifications heute, gestern.
    assert len([d for d in diffs if not d.expired()]) == 3


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
