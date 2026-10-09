from abc import ABC, abstractmethod
from datetime import datetime

from capabilities.models.booking import (
    BookingRequest,
    CalendarBusyInterval,
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
    def cancel_event(
        self,
        event_id: str,
    ) -> None:
        pass