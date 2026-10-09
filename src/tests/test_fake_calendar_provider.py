from datetime import (
    date,
    datetime,
    time,
)
from zoneinfo import ZoneInfo

from capabilities.booking.fake_calendar_provider import (
    FakeCalendarProvider,
)
from capabilities.models.booking import (
    BookingRequest,
    CalendarBusyInterval,
)


TIMEZONE = ZoneInfo("Europe/Madrid")


def test_fake_calendar_returns_busy_intervals():

    provider = FakeCalendarProvider(
        busy_intervals=[
            CalendarBusyInterval(
                start=datetime(
                    2026,
                    10,
                    16,
                    10,
                    0,
                    tzinfo=TIMEZONE,
                ),
                end=datetime(
                    2026,
                    10,
                    16,
                    10,
                    30,
                    tzinfo=TIMEZONE,
                ),
            )
        ]
    )

    intervals = provider.get_busy_intervals(
        start=datetime(
            2026,
            10,
            16,
            9,
            0,
            tzinfo=TIMEZONE,
        ),
        end=datetime(
            2026,
            10,
            16,
            14,
            0,
            tzinfo=TIMEZONE,
        ),
    )

    assert len(intervals) == 1


def test_fake_calendar_creates_booking_event():

    provider = FakeCalendarProvider()

    request = BookingRequest(
        first_name="Manuel",
        last_name="Buzón",
        email="manuel@example.com",
        service_id="haircut",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            11,
            0,
        ),
    )

    start = datetime(
        2026,
        10,
        16,
        11,
        0,
        tzinfo=TIMEZONE,
    )

    end = datetime(
        2026,
        10,
        16,
        11,
        30,
        tzinfo=TIMEZONE,
    )

    event_id = provider.create_booking_event(
        request=request,
        start=start,
        end=end,
        service_name="Corte",
    )

    assert event_id in provider.created_events

    assert (
        provider.created_events[
            event_id
        ]["service_name"]
        == "Corte"
    )

    assert len(provider.busy_intervals) == 1


def test_fake_calendar_cancel_event():

    provider = FakeCalendarProvider()

    request = BookingRequest(
        first_name="Carlos",
        last_name="Pérez",
        phone="600123123",
        service_id="haircut",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            12,
            0,
        ),
    )

    start = datetime(
        2026,
        10,
        16,
        12,
        0,
        tzinfo=TIMEZONE,
    )

    end = datetime(
        2026,
        10,
        16,
        12,
        30,
        tzinfo=TIMEZONE,
    )

    event_id = provider.create_booking_event(
        request=request,
        start=start,
        end=end,
        service_name="Corte",
    )

    provider.cancel_event(
        event_id
    )

    assert event_id not in provider.created_events
    assert provider.busy_intervals == []