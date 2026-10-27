import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from specs.storage import (
    load_website_spec,
    save_website_spec,
)
from specs.website_spec import WebsiteSpec


@pytest.fixture
def specification():
    return WebsiteSpec.model_validate(
        {
            "business": {
                "name": "Taller de prueba",
                "business_type": "taller",
                "location": "Sevilla",
                "services": ["Revisiones"],
                "main_goal": "Recibir consultas.",
                "desired_style": [],
            },
            "navigation": [],
            "primary_cta": None,
            "visual_direction": "Fotografía protagonista.",
            "color_palette": ["#D97706"],
            "typography_direction": "Títulos contundentes.",
            "sections": [],
            "capabilities": [],
            "missing_content": [],
            "missing_information": [],
            "missing_assets": [],
        }
    )


def test_saves_and_restores_full_specification(
    tmp_path,
    specification,
):
    path = tmp_path / "config" / "website_spec.json"

    save_website_spec(specification, path)

    restored = load_website_spec(path)

    assert restored == specification
    assert restored.color_palette == ["#D97706"]
    assert restored.visual_direction == "Fotografía protagonista."

    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["schema_version"] == 1


def test_missing_specification_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_website_spec(tmp_path / "website_spec.json")


@pytest.mark.parametrize("content", ["not-json", "{}"])
def test_rejects_corrupt_or_incomplete_snapshot(
    tmp_path,
    content,
):
    path = tmp_path / "website_spec.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValidationError):
        load_website_spec(path)


def test_rejects_unsupported_version(
    tmp_path,
    specification,
):
    path = tmp_path / "website_spec.json"

    path.write_text(
        json.dumps(
            {
                "schema_version": 99,
                "website_spec": specification.model_dump(
                    mode="json",
                ),
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_website_spec(path)


def test_failed_replacement_preserves_previous_snapshot(
    tmp_path,
    specification,
    monkeypatch,
):
    path = tmp_path / "website_spec.json"
    save_website_spec(specification, path)

    previous_content = path.read_bytes()

    updated = specification.model_copy(
        update={"visual_direction": "Una dirección diferente."},
    )

    def fail_replacement(self, target):
        raise OSError("Fallo simulado al sustituir el archivo.")

    monkeypatch.setattr(
        Path,
        "replace",
        fail_replacement,
    )

    with pytest.raises(OSError):
        save_website_spec(updated, path)

    assert path.read_bytes() == previous_content