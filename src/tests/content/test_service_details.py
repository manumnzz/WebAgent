
import pytest

from pydantic import ValidationError

from intake.models import ProjectInput
from content.builder import build_website_content


def test_project_input_accepts_service_details():
    project = ProjectInput(
        business_name="Iron Garage",
        business_description="Taller mecánico.",
        services=["Diagnóstico"],
        service_details=[
            {
                "name": "Diagnóstico",
                "description": "Revisión electrónica.",
                "price": "40 €",
            }
        ],
    )

    assert project.service_details[0].price == "40 €"


def test_project_input_preserves_legacy_services():
    project = ProjectInput(
        business_name="Iron Garage",
        business_description="Taller mecánico.",
        services=["Diagnóstico"],
    )

    assert project.services == ["Diagnóstico"]
    assert project.service_details == []


def test_project_input_rejects_unknown_service():
    with pytest.raises(ValidationError):
        ProjectInput(
            business_name="Iron Garage",
            business_description="Taller mecánico.",
            services=["Diagnóstico"],
            service_details=[
                {
                    "name": "Lavado",
                    "price": "20 €",
                }
            ],
        )


def test_project_input_rejects_duplicate_details():
    with pytest.raises(ValidationError):
        ProjectInput(
            business_name="Iron Garage",
            business_description="Taller mecánico.",
            services=["Diagnóstico"],
            service_details=[
                {"name": "Diagnóstico"},
                {"name": "Diagnóstico"},
            ],
        )


def test_project_input_rejects_unknown_detail_fields():
    with pytest.raises(ValidationError):
        ProjectInput(
            business_name="Iron Garage",
            business_description="Taller mecánico.",
            services=["Diagnóstico"],
            service_details=[
                {
                    "name": "Diagnóstico",
                    "discount": 50,
                }
            ],
        )
