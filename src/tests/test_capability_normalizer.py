
from specs.capability_spec import (
    CapabilityPlan,
    CapabilitySpec,
)

from intake.models import RequestedFeature

from capabilities.capability_plan_normalizer import (
    normalize_capability_plan,
)


def test_requested_capability_becomes_required():

    plan = CapabilityPlan(
        capabilities=[
            CapabilitySpec(
                type="whatsapp",
                required=False,
                reason="Facilita el contacto.",
            )
        ]
    )

    result = normalize_capability_plan(
        plan,
        [RequestedFeature.WHATSAPP],
    )

    assert len(result.capabilities) == 1
    assert result.capabilities[0].required is True


def test_missing_requested_capability_is_added():

    plan = CapabilityPlan(capabilities=[])

    result = normalize_capability_plan(
        plan,
        [RequestedFeature.CONTACT_FORM],
    )

    assert len(result.capabilities) == 1
    assert result.capabilities[0].type == "contact_form"
    assert result.capabilities[0].required is True


def test_optional_capability_remains_optional():

    plan = CapabilityPlan(
        capabilities=[
            CapabilitySpec(
                type="maps",
                required=False,
                reason="Facilita la localización.",
            )
        ]
    )

    result = normalize_capability_plan(plan, [])

    assert len(result.capabilities) == 1
    assert result.capabilities[0].required is False


def test_required_capability_remains_required():

    plan = CapabilityPlan(
        capabilities=[
            CapabilitySpec(
                type="booking",
                required=True,
                reason="Necesaria para reservar citas.",
            )
        ]
    )

    result = normalize_capability_plan(plan, [])

    assert result.capabilities[0].required is True


def test_duplicate_requested_features_are_not_added():

    plan = CapabilityPlan(capabilities=[])

    result = normalize_capability_plan(
        plan,
        [
            RequestedFeature.WHATSAPP,
            RequestedFeature.WHATSAPP,
        ],
    )

    assert len(result.capabilities) == 1


def test_original_plan_is_not_modified():

    plan = CapabilityPlan(
        capabilities=[
            CapabilitySpec(
                type="whatsapp",
                required=False,
                reason="Facilita el contacto.",
            )
        ]
    )

    result = normalize_capability_plan(
        plan,
        [RequestedFeature.WHATSAPP],
    )

    assert plan.capabilities[0].required is False
    assert result.capabilities[0].required is True


def test_multiple_requested_capabilities():

    plan = CapabilityPlan(
        capabilities=[
            CapabilitySpec(
                type="whatsapp",
                required=False,
                reason="Facilita el contacto.",
            ),
            CapabilitySpec(
                type="maps",
                required=False,
                reason="Facilita la localización.",
            ),
        ]
    )

    result = normalize_capability_plan(
        plan,
        [
            RequestedFeature.WHATSAPP,
            RequestedFeature.CONTACT_FORM,
        ],
    )

    capabilities = {
        capability.type: capability.required
        for capability in result.capabilities
    }

    assert capabilities == {
        "whatsapp": True,
        "maps": False,
        "contact_form": True,
    }


def test_empty_plan_without_requested_features():

    plan = CapabilityPlan(capabilities=[])

    result = normalize_capability_plan(plan, [])

    assert result.capabilities == []
