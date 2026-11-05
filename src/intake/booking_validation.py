from capabilities.models.booking import BookingConfigurationDraft


def validate_booking_submission(
        draft: BookingConfigurationDraft | None,
) -> None:

    """
    Validate that a submitted booking configuration
    contains the required operating schedule.
    
    Inquiry-only configurations do not require
    a weekly schedule.
    """

    if draft is None:
        return

    if not (draft.services or draft.pending_arrival_types):
        return

    schedule = draft.weekly_schedule or []

    expected_days = {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }

    actual_days = [day.weekday for day in schedule]

    if (
        len(actual_days) != len(expected_days)
        or set(actual_days) != expected_days
    ):
        raise ValueError(
            "Debes confirmar los siete días "
            "del horario de citas."
        )

    if not any(day.ranges for day in schedule):
        raise ValueError(
            "Debes indicar al menos un día "
            "con horario de citas disponible."
        )


