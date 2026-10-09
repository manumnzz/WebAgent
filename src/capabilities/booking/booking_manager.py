from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel

from capabilities.booking.availability import (
    calculate_available_slots,
)
from capabilities.booking.calendar_provider import (
    CalendarProvider,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingRequest,
    BookingService,
)


class BookingSlotUnavailableError(ValueError):
    pass


class BookingConfirmation(BaseModel):
    event_id: str

    service_id: str
    service_name: str

    start: datetime
    end: datetime


class BookingManager:

    def __init__(
        self,
        configuration: BookingConfiguration,
        calendar_provider: CalendarProvider,
    ):
        self.configuration = configuration
        self.calendar_provider = calendar_provider

    def _get_service(
        self,
        service_id: str,
    ) -> BookingService:

        for service in self.configuration.services:

            if service.id == service_id:
                return service

        raise ValueError(
            f"No existe el servicio de booking "
            f"'{service_id}'."
        )

    def get_available_slots(
        self,
        booking_date: date,
        service_id: str,
    ) -> list[datetime]:

        timezone = ZoneInfo(
            self.configuration.timezone
        )

        day_start = datetime.combine(
            booking_date,
            datetime.min.time(),
            tzinfo=timezone,
        )

        day_end = day_start + timedelta(
            days=1
        )

        busy_intervals = (
            self.calendar_provider
            .get_busy_intervals(
                start=day_start,
                end=day_end,
            )
        )

        return calculate_available_slots(
            configuration=self.configuration,
            booking_date=booking_date,
            service_id=service_id,
            busy_intervals=busy_intervals,
        )

    def create_booking(
        self,
        request: BookingRequest,
    ) -> BookingConfirmation:

        service = self._get_service(
            request.service_id
        )

        timezone = ZoneInfo(
            self.configuration.timezone
        )

        requested_start = datetime.combine(
            request.booking_date,
            request.booking_time,
            tzinfo=timezone,
        )

        available_slots = (
            self.get_available_slots(
                booking_date=request.booking_date,
                service_id=request.service_id,
            )
        )

        if requested_start not in available_slots:
            raise BookingSlotUnavailableError(
                "El horario solicitado ya no "
                "está disponible."
            )

        requested_end = (
            requested_start
            + timedelta(
                minutes=service.duration_minutes
            )
        )

        event_id = (
            self.calendar_provider
            .create_booking_event(
                request=request,
                start=requested_start,
                end=requested_end,
                service_name=service.name,
            )
        )

        return BookingConfirmation(
            event_id=event_id,
            service_id=service.id,
            service_name=service.name,
            start=requested_start,
            end=requested_end,
        )