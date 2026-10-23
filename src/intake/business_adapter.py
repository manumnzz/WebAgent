from agents.business_agent import BusinessProfile
from intake.models import ProjectInput
from intake.booking_adapter import (
    build_booking_draft_from_input,
    get_request_only_appointments,
)

def build_business_input(project_input: ProjectInput) -> str:
    return(
        "Analiza este encargo para crear la web de un negocio.\n"
        "Los campos estructurados contienen datos aportados "
        "por el cliente.\n"
        "La descripción y las notas pueden aportar información "
        "adicional.\n"
        "No inventes datos que no estén disponibles.\n"
        "Una opción con duración permite una reserva confirmada. Una opción "
        "marcada como pending_arrival permite proponer una hora de llegada, "
        "que el negocio debe confirmar. Una inquiry es una consulta sin "
        "hora. No prometas el tiempo de realización del trabajo.\n"
        "Conserva las funcionalidades solicitadas usando "
        "sus identificadores.\n\n"
        "ENCARGO DEL CLIENTE:\n"
        f"{project_input.model_dump_json(indent=2)}"
    )

def apply_explicit_business_data(
        business: BusinessProfile,
        project_input: ProjectInput,
) -> BusinessProfile:
    
    updated_business = business.model_copy(deep=True)

    updated_business.name = project_input.business_name

    explicit_fields = (
        "business_type",
        "location",
        "main_goal",
    )

    for field_name in explicit_fields:
        value = getattr(project_input, field_name)

        if value is not None:
            setattr(updated_business, field_name, value)

    if project_input.services:
        updated_business.services = list(
            project_input.services
        )

    if project_input.desired_style:
        updated_business.desired_style = list(
            project_input.desired_style
        )

    for field_name in (
        "phone",
        "whatsapp",
        "email",
        "address",
    ):
        value = getattr(project_input.contact, field_name)

        if value is not None:
            setattr(
                updated_business.contact,
                field_name,
                value,
            )

    requested_features = [
        feature.value
        for feature in project_input.requested_features
    ]

    updated_business.requested_features = list(
        dict.fromkeys(
            updated_business.requested_features 
            + 
            requested_features
        )
    )

    request_only = get_request_only_appointments(project_input)
    updated_business.appointment_request_types = request_only
    draft = build_booking_draft_from_input(project_input)
    updated_business.pending_arrival_types = (
        [option.name for option in draft.pending_arrival_types]
        if draft is not None else []
    )

    return updated_business
