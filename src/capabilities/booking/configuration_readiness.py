from capabilities.models.booking import (
    BookingConfigurationDraft,
    BookingMissingInformation,
)


WEEKDAYS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
}


def get_booking_missing_information(
    draft: BookingConfigurationDraft,
) -> BookingMissingInformation:

    missing_service_durations = [
        service.id
        for service in draft.services
        if service.duration_minutes is None
    ]

    schedule = draft.weekly_schedule or []
    confirmed_days = {
        day.weekday
        for day in schedule
    }

    schedule_is_complete = (
        len(schedule) == 7
        and confirmed_days == WEEKDAYS
        and any(day.ranges for day in schedule)
    )

    requires_hours = bool(draft.services or draft.pending_arrival_types)

    return BookingMissingInformation(
        service_durations=missing_service_durations,
        timezone=draft.timezone is None,
        weekly_schedule=requires_hours and not schedule_is_complete,
        slot_interval_minutes=(
            requires_hours and draft.slot_interval_minutes is None
        ),
    )
