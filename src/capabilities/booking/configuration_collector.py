from capabilities.models.booking import (
    BookingCollectedInformation,
    BookingConfigurationDraft,
)


def apply_booking_information(
    draft: BookingConfigurationDraft,
    information: BookingCollectedInformation,
) -> BookingConfigurationDraft:

    updated_draft = draft.model_copy(
        deep=True
    )

    services_by_id = {
        service.id: service
        for service in updated_draft.services
    }

    for service_id, duration in (
        information.service_durations.items()
    ):
        service = services_by_id.get(
            service_id
        )

        if service is None:
            raise ValueError(
                f"Servicio desconocido: {service_id}"
            )

        service.duration_minutes = duration

    if information.timezone is not None:
        updated_draft.timezone = (
            information.timezone
        )

    if information.weekly_schedule is not None:
        updated_draft.weekly_schedule = (
            information.weekly_schedule
        )

    if information.slot_interval_minutes is not None:
        updated_draft.slot_interval_minutes = (
            information.slot_interval_minutes
        )

    return updated_draft