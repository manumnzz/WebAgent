from agents.business_agent import BusinessProfile
from intake.models import ProjectInput

def build_business_input(project_input: ProjectInput) -> str:
    return(
        "Analiza este encargo para crear la web de un negocio.\n"
        "Los campos estructurados contienen datos aportados "
        "por el cliente.\n"
        "La descripción y las notas pueden aportar información "
        "adicional.\n"
        "No inventes datos que no estén disponibles.\n"
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

    return updated_business