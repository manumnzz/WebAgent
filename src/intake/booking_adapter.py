from capabilities.booking.configuration_builder import (
    build_booking_configuration_draft,
    build_booking_service_drafts,
)
from capabilities.booking.configuration_collector import (
    apply_booking_information,
)
from capabilities.models.booking import (
    BookingConfigurationDraft,
    PendingArrivalType,
    InquiryType,
)
from intake.models import ProjectInput, RequestedFeature


def get_request_only_appointments(project_input: ProjectInput) -> list[str]:
    """Return inquiries without an arrival time, including older saved inputs."""
    durations = (
        project_input.booking.service_durations
        if project_input.booking is not None
        else {}
    )
    return [
        service.name
        for service in build_booking_service_drafts(project_input.appointment_types)
        if service.id not in durations
        and (
            project_input.booking is None
            or project_input.booking.appointment_modes.get(service.id, "inquiry")
            == "inquiry"
        )
    ]


def build_booking_draft_from_input(
    project_input: ProjectInput,
) -> BookingConfigurationDraft | None:

    if RequestedFeature.BOOKING not in project_input.requested_features:
        return None

    # Generate IDs against the complete list before splitting. This keeps
    # duration keys stable even when a request-only option precedes a booking.
    draft = build_booking_configuration_draft(project_input.appointment_types)

    if project_input.booking is not None:
        draft = apply_booking_information(
            draft,
            project_input.booking,
        )

    modes = (
        project_input.booking.appointment_modes
        if project_input.booking is not None else {}
    )
    known_ids = {service.id for service in draft.services}
    unknown_modes = set(modes) - known_ids
    if unknown_modes:
        raise ValueError(f"Opción de cita desconocida: {sorted(unknown_modes)[0]}")
    conflicting = set(modes) & {
        service.id for service in draft.services
        if service.duration_minutes is not None
    }
    if conflicting:
        raise ValueError("Una cita con duración no puede tener otro modo.")

    draft.pending_arrival_types = [
        PendingArrivalType(id=service.id, name=service.name)
        for service in draft.services
        if service.duration_minutes is None
        and modes.get(service.id, "inquiry") == "pending_arrival"
    ]
    draft.inquiry_types = [
        InquiryType(id=service.id, name=service.name)
        for service in draft.services
        if service.duration_minutes is None
        and modes.get(service.id, "inquiry") == "inquiry"
    ]
    draft.services = [
        service for service in draft.services
        if service.duration_minutes is not None
    ]

    if not (draft.services or draft.pending_arrival_types or draft.inquiry_types):
        return None

    return draft
