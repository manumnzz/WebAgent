import json

import pytest

from capabilities.capability_registry import (
    CAPABILITY_REGISTRY,
    get_capability_definition,
)
from capabilities.placement_policy import (
    CapabilityPlacementPolicy,
)
from context.context_builders import (
    build_developer_context,
    build_developer_repair_context,
)
from specs.website_spec_builder import build_website_spec
from state.project_state import ProjectState


@pytest.fixture
def placement_state(monkeypatch):
    policy = CapabilityPlacementPolicy(
        max_instances=3,
        allowed_zones=("contact", "floating"),
    )

    definition = get_capability_definition("whatsapp")

    monkeypatch.setitem(
        CAPABILITY_REGISTRY,
        "whatsapp",
        definition.model_copy(
            update={"placement_policy": policy},
        ),
    )

    state = ProjectState.model_validate(
        {
            "business": {
                "name": "Taller de prueba",
                "business_type": "taller",
                "location": "Sevilla",
                "services": ["Revisiones"],
                "main_goal": "Recibir consultas por WhatsApp.",
                "desired_style": [],
            },
            "ux": {
                "sections": [],
                "navigation": [],
                "primary_cta": "Contactar",
                "missing_content": [],
            },
            "website_copy": {
                "sections": [],
            },
            "design": {
                "visual_direction": "Sencillo",
                "color_palette": [],
                "typography_direction": "Legible",
                "section_designs": [],
                "missing_assets": [],
                "missing_information": [],
            },
            "capability_plan": {
                "capabilities": [
                    {
                        "type": "whatsapp",
                        "required": True,
                        "reason": "Recibir consultas.",
                    }
                ],
            },
            "capability_inputs": {
                "whatsapp_number": "+34 612 345 678",
            },
            "validation": {
                "is_valid": False,
                "errors": [
                    {
                        "code": "capability_instance_limit_exceeded",
                        "file": "index.html",
                        "message": "Sobran enlaces de WhatsApp.",
                    }
                ],
            },
        }
    )

    state.website_spec = build_website_spec(state)

    return state, policy


@pytest.mark.parametrize(
    "context_builder",
    [
        build_developer_context,
        build_developer_repair_context,
    ],
)
def test_registry_policy_reaches_developer_context(
    placement_state,
    context_builder,
):
    state, policy = placement_state

    capability = state.website_spec.capabilities[0]

    assert capability.ready is True
    assert capability.placement_policy == policy

    context = context_builder(state)

    spec_text = context.split(
        "WEBSITE_SPEC:",
        maxsplit=1,
    )[1].lstrip()

    serialized_spec, _ = json.JSONDecoder().raw_decode(
        spec_text,
    )

    serialized_policy = serialized_spec[
        "capabilities"
    ][0]["placement_policy"]

    assert serialized_policy == policy.model_dump(
        mode="json",
    )

    assert "https://wa.me/34612345678" in context


def test_website_policy_is_independent_from_registry(
    placement_state,
):
    state, policy = placement_state

    website_policy = (
        state.website_spec.capabilities[0].placement_policy
    )

    assert website_policy is not policy

    website_policy.max_instances = 99
    website_policy.allowed_zones = ("footer",)

    registry_policy = get_capability_definition(
        "whatsapp",
    ).placement_policy

    assert registry_policy.max_instances == 3
    assert registry_policy.allowed_zones == (
        "contact",
        "floating",
    )