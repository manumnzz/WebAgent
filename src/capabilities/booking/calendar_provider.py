from abc import ABC, abstractmethod
from datetime import date, datetime

from capabilities.models.booking import (
    BookingRequest,
    CalendarBusyInterval,
    PendingArrivalRequest,
    InquiryRequest,
)

class CalendarProvider(ABC):

    @abstractmethod
    def get_busy_intervals(
        self,
        start: datetime,
        end: datetime,
    ) -> list[CalendarBusyInterval]:
        pass

    @abstractmethod
    def create_booking_event(
        self,
        request: BookingRequest,
        start: datetime,
        end: datetime,
        service_name: str,
    ) -> str: 
        """
        Crea el evento de reserva.
        
        Devuelve el identificador del evento creado.
        """
        pass

    @abstractmethod
    def create_pending_arrival_event(
        self,
        request: PendingArrivalRequest,
        start: datetime,
        end: datetime,
        option_name: str,
    ) -> str:
        """Store a proposed arrival without blocking free/busy or inviting the customer."""
        pass

    @abstractmethod
    def create_inquiry_event(
        self,
        request: InquiryRequest,
        day: date,
        option_name: str,
    ) -> str:
        """Store a contact inquiry as a non-blocking all-day pending item."""
        pass

    @abstractmethod
    def cancel_event(
        self,
        event_id: str,
    ) -> None:
        pass
