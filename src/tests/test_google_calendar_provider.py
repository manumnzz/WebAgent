from datetime import (
    date,
    datetime,
    time,
)
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

from capabilities.booking.google_calendar_provider import (
    GoogleCalendarProvider,
)
from capabilities.models.booking import (
    BookingRequest,
)


TIMEZONE = ZoneInfo(
    "Europe/Madrid"
)


def build_google_service_mock():

    service = MagicMock()

    events_resource = MagicMock()
    freebusy_resource = MagicMock()

    service.events.return_value = events_resource
    service.freebusy.return_value = freebusy_resource

    return service


def test_google_calendar_returns_busy_intervals():

    service = build_google_service_mock()

    (
        service
        .freebusy()
        .query()
        .execute
        .return_value
    ) = {
        "calendars": {
            "primary": {
                "busy": [
                    {
                        "start": (
                            "2026-10-16"
                            "T10:00:00+02:00"
                        ),
                        "end": (
                            "2026-10-16"
                            "T10:30:00+02:00"
                        ),
                    }
                ]
            }
        }
    }

    provider = GoogleCalendarProvider(
        service=service
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

    assert (
        intervals[0].start.time()
        == time(10, 0)
    )

    assert (
        intervals[0].end.time()
        == time(10, 30)
    )


def test_google_calendar_creates_event():

    service = build_google_service_mock()

    insert_request = MagicMock()

    insert_request.execute.return_value = {
        "id": "google-event-123"
    }

    service.events.return_value.insert.return_value = (
        insert_request
    )

    provider = GoogleCalendarProvider(
        service=service
    )

    request = BookingRequest(
        first_name="Manuel",
        last_name="Buzón",
        email="manuel@example.com",
        phone="600123123",
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
        notes="Degradado bajo.",
    )

    event_id = (
        provider.create_booking_event(
            request=request,
            start=datetime(
                2026,
                10,
                16,
                11,
                0,
                tzinfo=TIMEZONE,
            ),
            end=datetime(
                2026,
                10,
                16,
                11,
                30,
                tzinfo=TIMEZONE,
            ),
            service_name="Corte",
        )
    )

    assert event_id == (
        "google-event-123"
    )

    service.events.return_value.insert.assert_called_once()

    call_kwargs = (
        service
        .events
        .return_value
        .insert
        .call_args
        .kwargs
    )

    assert (
        call_kwargs["calendarId"]
        == "primary"
    )

    event = call_kwargs["body"]

    assert (
        event["summary"]
        == "Manuel Buzón — Corte"
    )

    assert (
        event[
            "extendedProperties"
        ][
            "private"
        ][
            "webagent_booking"
        ]
        == "true"
    )


def test_google_calendar_cancels_event():

    service = build_google_service_mock()

    provider = GoogleCalendarProvider(
        service=service
    )

    provider.cancel_event(
        "google-event-123"
    )

    (
        service
        .events()
        .delete
        .assert_called_once_with(
            calendarId="primary",
            eventId="google-event-123",
        )
    )