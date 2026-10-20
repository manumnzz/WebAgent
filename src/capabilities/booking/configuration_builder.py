from capabilities.booking.service_id import (
    generate_service_id,
)
from capabilities.models.booking import (
    BookingServiceDraft,
)
from capabilities.models.booking import (
    BookingServiceDraft,
    BookingConfigurationDraft,
)

def build_booking_service_drafts(
        service_names: list[str],
) -> list[BookingServiceDraft]:

    services: list[BookingServiceDraft] = []

    existing_ids: set[str] = set()
    seen_names: set[str] = set()

    for raw_name in service_names:

        name = raw_name.strip()

        if not name:
            continue

        normalized_name = name.casefold()

        if normalized_name in seen_names:
            continue

        service_id = generate_service_id(
            name,
            existing_ids=existing_ids,
        )

        services.append(
            BookingServiceDraft(
                id=service_id,
                name=name,
            )
        )

        existing_ids.add(service_id)
        seen_names.add(normalized_name)

    return services

def build_booking_configuration_draft(
    service_names: list[str],
) -> BookingConfigurationDraft:

    return BookingConfigurationDraft(
        services=build_booking_service_drafts(
            service_names
        )
    )

