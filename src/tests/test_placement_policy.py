import pytest
from pydantic import ValidationError

from capabilities.placement_policy import (
    CapabilityPlacementPolicy,
)


@pytest.mark.parametrize(
    "values",
    [
        {"max_instances": 0},
        {"allowed_zones": []},
        {"allowed_zones": ["contacto"]},
    ],
)
def test_rejects_invalid_placement_policies(values):
    with pytest.raises(ValidationError):
        CapabilityPlacementPolicy.model_validate(values)


def test_serializes_allowed_zones_as_json_array():
    policy = CapabilityPlacementPolicy(
        max_instances=2,
        allowed_zones=("hero", "contact"),
    )

    assert policy.model_dump(mode="json") == {
        "max_instances": 2,
        "allowed_zones": ["hero", "contact"],
    }


def test_allows_count_policy_without_zone_restrictions():
    policy = CapabilityPlacementPolicy(max_instances=2)

    assert policy.allowed_zones is None


