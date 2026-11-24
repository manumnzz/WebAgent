from specs.capability_spec import (
    CapabilityPlan,
    CapabilitySpec,
)

from intake.models import RequestedFeature

def normalize_capability_plan(
        plan: CapabilityPlan,
        requested_features: list[RequestedFeature],
) -> CapabilityPlan:

    capabilities_by_type = {}

    for capability in plan.capabilities:

        capability_type = capability.type

        if capability_type in capabilities_by_type:

            existing = capabilities_by_type[capability_type]

            existing.required = (
                existing.required or capability.required
            )

            if existing.reason != capability.reason:
                existing.reason += f" {capability.reason}"

        else:

            capabilities_by_type[capability_type] = (
                capability.model_copy()
            )

    for feature in requested_features:

        capability_type = feature.value

        if capability_type in capabilities_by_type:
            capabilities_by_type[capability_type].required = True

        else:

            capabilities_by_type[capability_type] = CapabilitySpec(
                type=capability_type,
                required=True,
                reason="Funcionalidad solicitada explícitamente por el cliente."
            )

    return CapabilityPlan(
        capabilities=list(capabilities_by_type.values())
    )