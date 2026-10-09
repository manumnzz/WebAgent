import os

from dotenv import load_dotenv

from api.booking_api import (
    create_booking_app,
)
from capabilities.booking.booking_manager import (
    BookingManager,
)
from capabilities.booking.config_loader import (
    load_booking_configuration,
)
from capabilities.booking.google_calendar_provider import (
    GoogleCalendarProvider,
)
from integrations.google_calendar_auth import (
    build_google_calendar_service,
)


load_dotenv()


BOOKING_CONFIG_PATH = os.getenv(
    "BOOKING_CONFIG_PATH",
    "config/booking.json",
)


configuration = load_booking_configuration(
    BOOKING_CONFIG_PATH
)

google_service = (
    build_google_calendar_service()
)

calendar_provider = (
    GoogleCalendarProvider(
        service=google_service,
    )
)

booking_manager = BookingManager(
    configuration=configuration,
    calendar_provider=calendar_provider,
)

app = create_booking_app(
    booking_manager
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "webagent-booking",
    }