from agents.business_agent import (
    BusinessProfile,
    ContactInfo,
)

from capabilities.capability_inputs import (
    CapabilityInputs,
)

from capabilities.capability_input_resolver import (
    resolve_business_capability_inputs,
)


def test_resolves_business_contact_into_capability_inputs():

    business = BusinessProfile(
        name="Iron Garage Sevilla",
        business_type="Taller de coches",
        location="Sevilla",
        services=[
            "Mecánica",
            "Personalización",
        ],
        main_goal="Conseguir clientes",
        desired_style=[
            "moderno",
            "agresivo",
        ],
        requested_features=[
            "Contacto por WhatsApp",
            "Formulario de contacto",
            "Google Maps",
        ],
        contact=ContactInfo(
            phone="+34 954 123 456",
            whatsapp="+34 612 345 678",
            email="contacto@irongarage.es",
            address="Calle Sierpes 15, Sevilla",
        ),
    )

    inputs = resolve_business_capability_inputs(
        business
    )

    assert (
        inputs.whatsapp_number
        == "+34 612 345 678"
    )

    assert (
        inputs.contact_destination
        == "contacto@irongarage.es"
    )

    assert (
        inputs.business_address
        == "Calle Sierpes 15, Sevilla"
    )

def test_preserves_existing_capability_inputs():

    business = BusinessProfile(
        name="Iron Garage Sevilla",
        business_type="Taller",
        location="Sevilla",
        services=[],
        main_goal=None,
        desired_style=[],
        contact=ContactInfo(
            whatsapp="+34 612 345 678",
        ),
    )

    existing_inputs = CapabilityInputs(
        gallery_assets=[
            "assets/car.jpg",
            "assets/workshop.jpg",
        ]
    )

    inputs = resolve_business_capability_inputs(
        business,
        existing_inputs,
    )

    assert (
        inputs.whatsapp_number
        == "+34 612 345 678"
    )

    assert inputs.gallery_assets == [
        "assets/car.jpg",
        "assets/workshop.jpg",
    ]