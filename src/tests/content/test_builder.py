
import pytest

from agents.business_agent import (
    BusinessProfile,
    ContactInfo,
)

from specs.website_spec import (
    WebsiteSpec,
    WebsiteSectionSpec,
)

from content.builder import build_website_content

from content.builder import (
    normalize_identifier,
    generate_unique_id,
)

from intake.models import ProjectInput

@pytest.fixture
def website_spec():
    business = BusinessProfile(
        name="Iron Garage",
        business_type="Taller mecánico",
        location="Sevilla",
        services=[
            "Diagnóstico electrónico",
            "Cambio de aceite",
            "Reparación de motor",
        ],
        main_goal="Conseguir clientes",
        desired_style=["premium", "dark"],
        contact=ContactInfo(
            phone="954123456",
            email="info@irongarage.es",
            address="Sevilla",
        ),
    )

    sections = [
        WebsiteSectionSpec(
            name="Hero",
            purpose="Presentación del negocio",
            headline="Pasión por el motor",
            body="Especialistas en mecánica.",
            cta="Contactar",
            copy_ready=True,
            missing_copy_requirements=[],
            layout="split",
            visual_notes="Estilo oscuro",
            required_inputs=[],
        ),
        WebsiteSectionSpec(
            name="Servicios",
            purpose="Mostrar servicios",
            headline="Nuestros servicios",
            body="Cuidamos tu vehículo.",
            cta=None,
            copy_ready=True,
            missing_copy_requirements=[],
            layout="grid",
            visual_notes="Tarjetas visuales",
            required_inputs=[],
        ),
    ]

    return WebsiteSpec(
        business=business,
        navigation=["Inicio", "Servicios"],
        primary_cta="Contactar",
        visual_direction="Premium automotive",
        color_palette=["#111111", "#FF6600"],
        typography_direction="Modern sans-serif",
        sections=sections,
        capabilities=[],
        missing_content=[],
        missing_information=[],
        missing_assets=[],
    )


def test_builder_preserves_business_information(
    website_spec,
):
    content = build_website_content(website_spec)

    assert content.business_name == "Iron Garage"
    assert content.contact.phone == "954123456"
    assert len(content.services) == 3

def test_builder_does_not_invent_prices(website_spec):
    content = build_website_content(website_spec)

    assert all(
        service.price is None
        for service in content.services
    )



def test_builder_generates_unique_service_ids(
    website_spec,
):
    content = build_website_content(website_spec)

    ids = [service.id for service in content.services]

    assert len(ids) == len(set(ids))
    assert "diagnostico-electronico" in ids
    assert "cambio-de-aceite" in ids


def test_builder_is_deterministic(website_spec):
    first = build_website_content(website_spec)
    second = build_website_content(website_spec)

    assert first == second


def test_builder_does_not_mutate_original_contact(
    website_spec,
):
    content = build_website_content(website_spec)

    content.contact.phone = "600111222"

    assert (
        website_spec.business.contact.phone
        == "954123456"
    )


def test_builder_handles_duplicate_service_names(
    website_spec,
):
    website_spec.business.services = [
        "Diagnóstico",
        "Diagnóstico",
    ]

    content = build_website_content(website_spec)

    ids = [service.id for service in content.services]

    assert ids == [
        "diagnostico",
        "diagnostico-2",
    ]



def test_builder_rejects_missing_business_name(
    website_spec,
):
    website_spec.business.name = None

    with pytest.raises(ValueError):
        build_website_content(website_spec)


def test_builder_round_trip_json(website_spec):
    content = build_website_content(website_spec)

    restored = type(content).model_validate_json(
        content.model_dump_json()
    )

    assert restored == content


def test_normalize_identifier_removes_accents():
    assert (
        normalize_identifier("Reparación Mecánica")
        == "reparacion-mecanica"
    )


def test_normalize_identifier_removes_symbols():
    assert (
        normalize_identifier("Cambio de aceite!!!")
        == "cambio-de-aceite"
    )


def test_generate_unique_id_avoids_collisions():
    used_ids = set()

    first = generate_unique_id(
        "Diagnóstico",
        used_ids,
    )

    second = generate_unique_id(
        "Diagnóstico",
        used_ids,
    )

    third = generate_unique_id(
        "Diagnóstico-2",
        used_ids,
    )

    assert first == "diagnostico"
    assert second == "diagnostico-2"
    assert third == "diagnostico-2-2"


def test_generate_unique_id_rejects_empty_value():
    with pytest.raises(ValueError):
        generate_unique_id(
            "!!!",
            set(),
        )


def test_builder_does_not_extract_editorial_sections(
    website_spec,
):
    content = build_website_content(website_spec)

    serialized = content.model_dump()

    assert "sections" not in serialized

    assert "Pasión por el motor" not in (
        content.model_dump_json()
    )


def test_builder_preserves_editorial_source(
    website_spec,
):
    original_headline = (
        website_spec.sections[0].headline
    )

    content = build_website_content(website_spec)

    content.services[0].name = "Nuevo servicio"

    assert (
        website_spec.sections[0].headline
        == original_headline
    )


def test_builder_only_contains_operational_fields(
    website_spec,
):
    content = build_website_content(website_spec)

    assert set(type(content).model_fields) == {
        "schema_version",
        "business_name",
        "contact",
        "services",
        "opening_hours",
        "gallery",
    }



def test_builder_preserves_service_details(website_spec):
    project = ProjectInput(
        business_name="Iron Garage",
        business_description="Taller mecánico.",
        services=["Diagnóstico electrónico"],
        service_details=[
            {
                "name": "Diagnóstico electrónico",
                "description": "Lectura de averías.",
                "price": "40 €",
            }
        ],
    )

    content = build_website_content(
        website_spec,
        project,
    )

    service = content.services[0]

    assert service.name == "Diagnóstico electrónico"
    assert service.description == "Lectura de averías."
    assert service.price == "40 €"


def test_builder_does_not_invent_missing_details(
    website_spec,
):
    project = ProjectInput(
        business_name="Iron Garage",
        business_description="Taller mecánico.",
        services=["Diagnóstico electrónico"],
    )

    content = build_website_content(
        website_spec,
        project,
    )

    assert all(
        service.price is None
        for service in content.services
    )

    assert all(
        service.description is None
        for service in content.services
    )


def test_builder_preserves_original_service_details(
    website_spec,
):
    project = ProjectInput(
        business_name="Iron Garage",
        business_description="Taller mecánico.",
        services=["Diagnóstico electrónico"],
        service_details=[
            {
                "name": "Diagnóstico electrónico",
                "price": "40 €",
            }
        ],
    )

    content = build_website_content(
        website_spec,
        project,
    )

    content.services[0].price = "60 €"

    assert project.service_details[0].price == "40 €"


def test_builder_preserves_services_without_details(
    website_spec,
):
    project = ProjectInput(
        business_name="Iron Garage",
        business_description="Taller mecánico.",
        services=[
            "Diagnóstico electrónico",
            "Cambio de aceite",
            "Reparación de motor",
        ],
        service_details=[
            {
                "name": "Diagnóstico electrónico",
                "price": "40 €",
            }
        ],
    )

    content = build_website_content(
        website_spec,
        project,
    )

    assert len(content.services) == 3

    assert content.services[0].price == "40 €"
    assert content.services[1].price is None
    assert content.services[2].price is None
