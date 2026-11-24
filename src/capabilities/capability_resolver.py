from capabilities.capability_implementation import (
    CapabilityImplementation,
)
from capabilities.implementation_registry import (
    build_capability_implementation,
)
from specs.website_spec import WebsiteSpec

def resolve_ready_capability_implementations(
    website_spec: WebsiteSpec,
) -> list[CapabilityImplementation]:

    implementations = []

    for capability in website_spec.capabilities:

        inputs = capability.input_values
        if not capability.ready:
            continue

        implementation = build_capability_implementation(
            capability_type=capability.type,
            input_values=inputs,
        )

        implementations.append(
            implementation
        )

    return implementations
