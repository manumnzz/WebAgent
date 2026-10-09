from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from capabilities.models.booking import (
    BookingConfiguration,
    BookingService,
    CalendarBusyInterval,
)


WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def _get_service(
    configuration: BookingConfiguration,
    service_id: str,
) -> BookingService:

    for service in configuration.services:
        if service.id == service_id:
            return service

    raise ValueError(
        f"No existe el servicio de booking '{service_id}'."
    )


def _intervals_overlap(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime,
) -> bool:

    return (
        start_a < end_b
        and end_a > start_b
    )


def calculate_available_slots(
    configuration: BookingConfiguration,
    booking_date: date,
    service_id: str,
    busy_intervals: list[CalendarBusyInterval],
) -> list[datetime]:

    service = _get_service(
        configuration,
        service_id,
    )

    weekday = WEEKDAYS[
        booking_date.weekday()
    ]

    day_schedules = [
        schedule
        for schedule in configuration.weekly_schedule
        if schedule.weekday == weekday
    ]

    if not day_schedules:
        return []

    timezone = ZoneInfo(
        configuration.timezone
    )

    service_duration = timedelta(
        minutes=service.duration_minutes
    )

    slot_interval = timedelta(
        minutes=configuration.slot_interval_minutes
    )

    available_slots: list[datetime] = []

    for schedule in day_schedules:

        for time_range in schedule.ranges:

            range_start = datetime.combine(
                booking_date,
                time_range.start,
                tzinfo=timezone,
            )

            range_end = datetime.combine(
                booking_date,
                time_range.end,
                tzinfo=timezone,
            )

            candidate_start = range_start

            while (
                candidate_start + service_duration
                <= range_end
            ):

                candidate_end = (
                    candidate_start
                    + service_duration
                )

                overlaps = any(
                    _intervals_overlap(
                        candidate_start,
                        candidate_end,
                        busy.start.astimezone(
                            timezone
                        ),
                        busy.end.astimezone(
                            timezone
                        ),
                    )
                    for busy in busy_intervals
                )

                if not overlaps:
                    available_slots.append(
                        candidate_start
                    )

                candidate_start += slot_interval

    return available_slots