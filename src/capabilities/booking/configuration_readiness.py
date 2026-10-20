from capabilities.models.booking import (
    BookingConfigurationDraft,
    BookingMissingInformation,
)


def get_booking_missing_information(
    draft: BookingConfigurationDraft,
) -> BookingMissingInformation:

    missing_service_durations = [
        service.id
        for service in draft.services
        if service.duration_minutes is None
    ]

    return BookingMissingInformation(
        service_durations=missing_service_durations,
        timezone=draft.timezone is None,
        weekly_schedule=(
            draft.weekly_schedule is None
        ),
        slot_interval_minutes=(
            draft.slot_interval_minutes is None
        ),
    )