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
    PendingArrivalRequest,
    PendingArrivalType,
    InquiryRequest,
)


class BookingSlotUnavailableError(ValueError):
    pass


class BookingConfirmation(BaseModel):
    event_id: str

    service_id: str
    service_name: str

    start: datetime
    end: datetime


class PendingArrivalConfirmation(BaseModel):
    event_id: str
    request_type_id: str
    proposed_start: datetime
    status: str = "pending"


class InquiryConfirmation(BaseModel):
    event_id: str
    request_type_id: str
    status: str = "pending"


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

    def _get_pending_option(self, option_id: str) -> PendingArrivalType:
        for option in self.configuration.pending_arrival_types:
            if option.id == option_id:
                return option
        raise ValueError(f"No existe la opción de llegada '{option_id}'.")

    def get_available_arrival_slots(
        self,
        booking_date: date,
        option_id: str,
    ) -> list[datetime]:
        self._get_pending_option(option_id)
        # The slot represents time for receiving the customer, not the
        # duration of the repair or of the vehicle's stay.
        arrival_service = BookingService(
            id=option_id,
            name="Hora de llegada propuesta",
            duration_minutes=self.configuration.slot_interval_minutes,
        )
        temporary_configuration = self.configuration.model_copy(
            update={"services": [*self.configuration.services, arrival_service]}
        )
        return BookingManager(
            temporary_configuration, self.calendar_provider
        ).get_available_slots(booking_date, option_id)

    def create_pending_arrival(
        self,
        request: PendingArrivalRequest,
    ) -> PendingArrivalConfirmation:
        option = self._get_pending_option(request.service_id)
        timezone = ZoneInfo(self.configuration.timezone)
        proposed_start = datetime.combine(
            request.booking_date, request.booking_time, tzinfo=timezone
        )
        if proposed_start <= datetime.now(timezone):
            raise ValueError("Elige una hora futura para la entrega.")
        if proposed_start not in self.get_available_arrival_slots(
            request.booking_date, request.service_id
        ):
            raise BookingSlotUnavailableError(
                "Esa hora de llegada ya no está disponible."
            )

        proposed_end = proposed_start + timedelta(
            minutes=self.configuration.slot_interval_minutes
        )
        event_id = self.calendar_provider.create_pending_arrival_event(
            request=request,
            start=proposed_start,
            end=proposed_end,
            option_name=option.name,
        )
        return PendingArrivalConfirmation(
            event_id=event_id,
            request_type_id=option.id,
            proposed_start=proposed_start,
        )

    def create_inquiry(self, request: InquiryRequest) -> InquiryConfirmation:
        option = next(
            (item for item in self.configuration.inquiry_types
             if item.id == request.service_id),
            None,
        )
        if option is None:
            raise ValueError(f"No existe la consulta '{request.service_id}'.")
        today = datetime.now(ZoneInfo(self.configuration.timezone)).date()
        event_id = self.calendar_provider.create_inquiry_event(
            request=request, day=today, option_name=option.name,
        )
        return InquiryConfirmation(
            event_id=event_id, request_type_id=option.id,
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
