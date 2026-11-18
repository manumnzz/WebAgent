from capabilities.capability_implementation import (
    CapabilityImplementation,
)
from capabilities.implementation_registry import (
    build_capability_implementation,
)
from specs.website_spec import WebsiteSpec

EDITABLE_CAPABILITIES = {"whatsapp", "maps", "contact_form", "gallery"}


def resolve_ready_capability_implementations(
    website_spec: WebsiteSpec,
    *,
    editable_content: bool = False,
) -> list[CapabilityImplementation]:

    implementations = []

    for capability in website_spec.capabilities:

        inputs = capability.input_values
        if not capability.ready:
            if not editable_content or capability.type != "gallery":
                continue
            inputs = {"gallery_assets": []}

        if editable_content and capability.type in EDITABLE_CAPABILITIES:
            inputs = {**inputs, "editable": True}

        implementation = build_capability_implementation(
            capability_type=capability.type,
            input_values=inputs,
        )

        implementations.append(
            implementation
        )

    return implementations
