from collections.abc import Callable

from capabilities.capability_implementation import (
    CapabilityImplementation,
)

from specs.capability_spec import CapabilityType

from capabilities.implementations.whatsapp import (
    build_whatsapp_implementation,
)
from capabilities.implementations.maps import (
    build_maps_implementation,
)


CapabilityBuilder = Callable[..., CapabilityImplementation]

CAPABILITY_IMPLEMENTATION_REGISTRY: dict[
    CapabilityType,
    CapabilityBuilder,
] = {
    "whatsapp": build_whatsapp_implementation,
    "maps": build_maps_implementation
}

def get_capability_implementation_builder(
        capability_type: CapabilityType,
) -> CapabilityBuilder:

    builder = CAPABILITY_IMPLEMENTATION_REGISTRY.get(
        capability_type
    )

    if builder is None:
        raise ValueError(
            f"No existe implementación para la capability "
            f"'{capability_type}'."
        )
    return builder

def build_capability_implementation(
        capability_type: CapabilityType,
        input_values: dict,
) -> CapabilityImplementation:

    builder = get_capability_implementation_builder(
        capability_type
    )

    return builder(**input_values)

