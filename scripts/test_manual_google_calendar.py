from datetime import (
    date,
    time,
)

from capabilities.booking.booking_manager import (
    BookingManager,
)
from capabilities.booking.google_calendar_provider import (
    GoogleCalendarProvider,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingDaySchedule,
    BookingRequest,
    BookingService,
    BookingTimeRange,
)
from integrations.google_calendar_auth import (
    build_google_calendar_service,
)


service = build_google_calendar_service()

calendar_provider = (
    GoogleCalendarProvider(
        service=service
    )
)

configuration = BookingConfiguration(
    timezone="Europe/Madrid",
    services=[
        BookingService(
            id="haircut",
            name="Corte",
            duration_minutes=30,
        )
    ],
    weekly_schedule=[
        BookingDaySchedule(
            weekday="friday",
            ranges=[
                BookingTimeRange(
                    start=time(9, 0),
                    end=time(14, 0),
                )
            ],
        )
    ],
    slot_interval_minutes=30,
)

manager = BookingManager(
    configuration=configuration,
    calendar_provider=calendar_provider,
)

request = BookingRequest(
    first_name="Test",
    last_name="WebAgent",
    email="test@example.com",
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

confirmation = manager.create_booking(
    request
)

print(
    confirmation.model_dump_json(
        indent=2
    )
)