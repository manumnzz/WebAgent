import pytest
from pydantic import ValidationError

from specs.design_system import DesignSystem


@pytest.mark.parametrize(
    "values",
    [
        {"colors": {"accent": "azul"}},
        {"layout": {"content_max_width_px": 0}},
        {"motion": {"duration_ms": -1}},
        {"motion": {"respect_reduced_motion": False}},
    ],
)
def test_rejects_invalid_design_system(values):
    with pytest.raises(ValidationError):
        DesignSystem.model_validate(values)