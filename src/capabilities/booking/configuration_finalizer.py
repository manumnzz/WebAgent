from capabilities.booking.configuration_readiness import (
    get_booking_missing_information,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingConfigurationDraft,
    BookingService,
)


def finalize_booking_configuration(
    draft: BookingConfigurationDraft,
) -> BookingConfiguration:

    missing = get_booking_missing_information(
        draft
    )

    if not missing.is_complete:
        raise ValueError(
            "No se puede finalizar BookingConfiguration: "
            "todavía falta información."
        )

    if draft.timezone is None:
        raise ValueError(
            "Booking necesita timezone."
        )

    if draft.weekly_schedule is None:
        raise ValueError(
            "Booking necesita weekly_schedule."
        )

    if draft.slot_interval_minutes is None:
        raise ValueError(
            "Booking necesita slot_interval_minutes."
        )

    services: list[BookingService] = []

    for service in draft.services:

        if service.duration_minutes is None:
            raise ValueError(
                f"El servicio '{service.id}' "
                "no tiene duración."
            )

        services.append(
            BookingService(
                id=service.id,
                name=service.name,
                duration_minutes=(
                    service.duration_minutes
                ),
            )
        )

    return BookingConfiguration(
        timezone=draft.timezone,
        services=services,
        weekly_schedule=draft.weekly_schedule,
        slot_interval_minutes=(
            draft.slot_interval_minutes
        ),
    )