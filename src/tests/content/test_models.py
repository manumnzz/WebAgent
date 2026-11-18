
import pytest
from pydantic import ValidationError

from content.models import (
    WebsiteContent,
    ServiceContent,
)


def test_website_content_serialization():
    content = WebsiteContent(
        business_name="Iron Garage",
        services=[
            ServiceContent(
                id="diagnostico",
                name="Diagnóstico",
                price="40 €",
            )
        ],
    )

    serialized = content.model_dump_json()
    restored = WebsiteContent.model_validate_json(
        serialized
    )

    assert restored == content
    assert restored.schema_version == 2
    assert restored.services[0].price == "40 €"


def test_website_content_requires_business_name():
    with pytest.raises(ValidationError):
        WebsiteContent(business_name="")


def test_service_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ServiceContent(
            id="diagnostico",
            name="Diagnóstico",
            invented_field="invalid",
        )


def test_website_content_rejects_duplicate_service_ids():
    with pytest.raises(ValidationError):
        WebsiteContent(
            business_name="Iron Garage",
            services=[
                ServiceContent(
                    id="diagnostico",
                    name="Diagnóstico electrónico",
                ),
                ServiceContent(
                    id="diagnostico",
                    name="Diagnóstico de motor",
                ),
            ],
        )



def test_website_content_rejects_editorial_sections():
    with pytest.raises(ValidationError):
        WebsiteContent(
            business_name="Iron Garage",
            sections=[
                {
                    "id": "hero",
                    "headline": "Pasión por el motor",
                }
            ],
        )


def test_service_description_has_length_limit():
    with pytest.raises(ValidationError):
        ServiceContent(
            id="diagnostico",
            name="Diagnóstico",
            description="A" * 501,
        )


def test_website_content_rejects_old_schema_version():
    with pytest.raises(ValidationError):
        WebsiteContent(
            schema_version=1,
            business_name="Iron Garage",
        )



def test_website_content_preserves_contact():
    content = WebsiteContent(
        business_name="Iron Garage",
        contact={
            "phone": "954123456",
            "email": "info@irongarage.es",
            "address": "Sevilla",
        },
    )

    restored = WebsiteContent.model_validate_json(
        content.model_dump_json()
    )

    assert restored.contact.phone == "954123456"
    assert restored.contact.email == "info@irongarage.es"
    assert restored.contact.address == "Sevilla"


def test_website_content_has_independent_contact():
    first = WebsiteContent(
        business_name="Iron Garage"
    )

    second = WebsiteContent(
        business_name="Fisio Alameda"
    )

    first.contact.phone = "954123456"

    assert second.contact.phone is None

def test_website_content_rejects_unknown_contact_fields():
    with pytest.raises(ValidationError):
        WebsiteContent(
            business_name="Iron Garage",
            contact={
                "phone": "954123456",
                "instagram": "@irongarage",
            },
        )