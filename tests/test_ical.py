import pytest
from arrow import Arrow

from ical import Event, EventDiff, EventList, compare, format_diffs


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


def test_diff(diffs):
    """
    Test that it captures differences between iCal files
    """
    # all events
    assert (len(diffs)) == 6

    # no expired events:
    # Feature Request Prokrastibot:
    # "Termin entfällt" > 5 Monate her nicht mehr notifizieren. Oder
    # nach 6m-1 Tag aus der eigenen Datenhaltung löschen. Sieht so aus
    # als würde alles was 6 Monate alt ist aus dem Kalender entfernt
    # werden, siehe notifications heute, gestern.
    assert len([d for d in diffs if not d.expired()]) == 3


def test_format(diffs):
    """
    Test that it formats lists of diffs
    """
    assert (
        format_diffs(diffs)
        == """🟢 Neuer Termin
🔥 Test Event - new and upcoming
🕒 Mi, 15.09.2032 12:00 CEST bis Mi, 15.09.2032 13:00 CEST
🏫 Muster Weg  456, 50123 Köln, K - Muster Hochschule für neue Termine, Kalender und Bots, Raum: K/HTKB 1.23
〰
🔴 Termin entfällt
🔥 Test Event - removed and upcoming
🕒 Mi, 15.09.2032 15:00 CEST bis Mi, 15.09.2032 16:00 CEST
🏫 Muster Weg  456, 50123 Köln, K - Muster Hochschule für entfernte Termine, Kalender und Bots, Raum: K/HTKB 1.23
〰
🟡 Terminänderung
🔥 Test Event - changed and upcoming, after (umbenannt von Test Event - changed and upcoming, before)
🕒 Beginn verlegt auf Do, 16.09.2032 18:00 CEST (von Mi, 15.09.2032 18:00 CEST)
🕟 Ende verlegt auf Do, 16.09.2032 19:00 CEST (von Mi, 15.09.2032 19:00 CEST)
🏫 Verlegt nach 👉 Muster Weg  789, 50123 Köln, K - Muster Hochschule für geänderte Termine, Kalender und Bots, Raum: K/HTKB 1.78 👈 (ursprünglich Muster Weg  456, 50123 Köln, K - Muster Hochschule für geänderte Termine, Kalender und Bots, Raum: K/HTKB 1.23)
〰
"""
    )


@pytest.fixture
def calfile_large() -> EventList:
    return EventList.from_file(
        "tests/integration/fixtures/campus-termine-2022-10-31.ics"
    )


@pytest.fixture
def diffs(calfile_before, calfile_after) -> list[EventDiff]:
    return compare(calfile_before, calfile_after)


@pytest.fixture
def calfile_before() -> EventList:
    return EventList.from_file("tests/integration/fixtures/before.ics")


@pytest.fixture
def calfile_after() -> EventList:
    return EventList.from_file("tests/integration/fixtures/after.ics")
