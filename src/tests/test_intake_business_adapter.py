from agents.business_agent import BusinessProfile
from intake.business_adapter import (
    apply_explicit_business_data,
    build_business_input,
)
from intake.models import (
    BusinessContactInput,
    ProjectInput,
    RequestedFeature,
)


def test_explicit_data_overrides_agent_result_without_mutating_it():
    project_input = ProjectInput(
        business_name="Apex Barber Club",
        business_description="Barbería en Sevilla.",
        services=["Corte", "Corte y barba"],
        contact=BusinessContactInput(
            whatsapp="+34612345678",
        ),
        requested_features=[
            RequestedFeature.BOOKING,
        ],
    )

    agent_result = BusinessProfile(
        name="Nombre incorrecto",
        business_type="barbería",
        location="Sevilla",
        services=["Servicio incorrecto"],
        main_goal="Conseguir reservas",
        desired_style=["moderno"],
        requested_features=["booking", "whatsapp"],
        contact={
            "whatsapp": "+34000000000",
            "email": "contacto@example.com",
        },
    )

    result = apply_explicit_business_data(
        agent_result,
        project_input,
    )

    assert result.name == "Apex Barber Club"
    assert result.services == ["Corte", "Corte y barba"]
    assert result.contact.whatsapp == "+34612345678"

    # Conservamos información no aportada en campos explícitos.
    assert result.location == "Sevilla"
    assert result.contact.email == "contacto@example.com"

    assert result.requested_features == [
        "booking",
        "whatsapp",
    ]

    # El objeto original sigue intacto.
    assert agent_result.name == "Nombre incorrecto"
    assert agent_result.contact.whatsapp == "+34000000000"


def test_business_input_contains_client_information():
    project_input = ProjectInput(
        business_name="Apex Barber Club",
        business_description="Barbería en Sevilla.",
        requested_features=[
            RequestedFeature.BOOKING,
        ],
    )

    context = build_business_input(project_input)

    assert "Apex Barber Club" in context
    assert "Barbería en Sevilla." in context
    assert '"booking"' in context