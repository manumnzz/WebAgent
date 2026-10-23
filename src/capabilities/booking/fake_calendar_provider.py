from datetime import date, datetime
from uuid import uuid4

from capabilities.booking.calendar_provider import (
    CalendarProvider,
)
from capabilities.models.booking import (
    BookingRequest,
    CalendarBusyInterval,
    PendingArrivalRequest,
    InquiryRequest,
)

class FakeCalendarProvider(CalendarProvider):

    def __init__(
            self,
            busy_intervals: list[CalendarBusyInterval] | None = None,
    ):
        self.busy_intervals = (
            busy_intervals or []
        )

        self.created_events: dict[
            str,
            dict,
        ] = {}
        self.pending_events: dict[str, dict] = {}
        self.inquiry_events: dict[str, dict] = {}

    def get_busy_intervals(
            self,
            start: datetime,
            end: datetime,
    ) -> list[CalendarBusyInterval]:
        
        return [
            interval
            for interval in self.busy_intervals
            if (
                interval.start < end
                and interval.end > start
            )
        ]

    def create_booking_event(
            self,
            request: BookingRequest,
            start: datetime,
            end: datetime,
            service_name:str,
    ) -> str:

      event_id = str(uuid4())

      self.created_events[event_id] ={
          "request": request,
          "start": start,
          "end": end,
          "service_name": service_name,
      }  

      self.busy_intervals.append(
          CalendarBusyInterval(
              start=start,
              end=end,
          )
      )

      return event_id

    def create_pending_arrival_event(
        self,
        request: PendingArrivalRequest,
        start: datetime,
        end: datetime,
        option_name: str,
    ) -> str:
        event_id = str(uuid4())
        self.pending_events[event_id] = {
            "request": request,
            "start": start,
            "end": end,
            "option_name": option_name,
            "status": "pending",
        }
        return event_id

    def create_inquiry_event(
        self,
        request: InquiryRequest,
        day: date,
        option_name: str,
    ) -> str:
        event_id = str(uuid4())
        self.inquiry_events[event_id] = {
            "request": request,
            "day": day,
            "option_name": option_name,
            "status": "pending",
        }
        return event_id

    def cancel_event(
            self,
            event_id: str,
    ) -> None:

        if event_id not in self.created_events:
            raise ValueError(
                f"No existe el evento '{event_id}'."
            )

        event = self.created_events.pop(
            event_id
        )

        self.busy_intervals = [
            interval
            for interval in self.busy_intervals
            if not (
                interval.start
                == event["start"]
                and interval.end 
                == event["end"]
            )
        ]
