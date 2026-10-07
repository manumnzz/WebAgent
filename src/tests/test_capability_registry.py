from typing import get_args

from capabilities.capability_registry import (
    CAPABILITY_REGISTRY,
    get_capability_definition,
)
from specs.capability_spec import CapabilityType


def test_booking_exists_in_registry():
    definition = get_capability_definition("booking")

    assert definition.type == "booking"


def test_all_definitions_have_description():
    for definition in CAPABILITY_REGISTRY.values():
        assert definition.description.strip()


def test_all_definitions_have_developer_requirements():
    for definition in CAPABILITY_REGISTRY.values():
        assert definition.developer_requirements


def test_registry_contains_all_capability_types():
    capability_types = set(get_args(CapabilityType))
    registry_types = set(CAPABILITY_REGISTRY.keys())

    assert registry_types == capability_types