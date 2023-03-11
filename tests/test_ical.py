import ical
from arrow import Arrow


def test_ended():
    now = Arrow.now()

    event = ical.Event(
        uid="1234",
        tstamp=now,
        summary="Just a test",
        location="here",
        start=now.shift(minutes=-10),
        end=now.shift(minutes=-5),
    )
    assert event.ended()

    event = ical.Event(
        uid="1234",
        tstamp=now,
        summary="Just a test",
        location="here",
        start=now.shift(minutes=5),
        end=now.shift(minutes=10),
    )
    assert not event.ended()
