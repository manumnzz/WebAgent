import json

import pytest
from pydantic import ValidationError

from intake.loader import load_project_input
from intake.models import RequestedFeature


def test_load_project_input(tmp_path):
    input_file = tmp_path / "project_input.json"

    input_file.write_text(
        json.dumps({
            "business_name": "Barbería Prueba",
            "business_description": "Barbería en Sevilla.",
            "requested_features": ["booking"],
        }),
        encoding="utf-8",
    )

    result = load_project_input(input_file)

    assert result.business_name == "Barbería Prueba"
    assert result.requested_features == [
        RequestedFeature.BOOKING
    ]
    assert result.services == []


def test_load_project_input_rejects_unknown_feature(tmp_path):
    input_file = tmp_path / "project_input.json"

    input_file.write_text(
        json.dumps({
            "business_name": "Barbería Prueba",
            "business_description": "Barbería en Sevilla.",
            "requested_features": ["unknown_feature"],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_project_input(input_file)