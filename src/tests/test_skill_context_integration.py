import json
from unittest.mock import MagicMock

import pytest

from agent_skills import context as skill_context
from context.context_builders import (
    build_design_context,
    build_developer_context,
    build_developer_repair_context,
)


@pytest.fixture
def skills_directory(tmp_path, monkeypatch):
    for name, instructions in [
        ("frontend-design", "SELECTED_DESIGN_INSTRUCTIONS"),
        ("visual-review", "UNSELECTED_REVIEW_INSTRUCTIONS"),
    ]:
        directory = tmp_path / name
        directory.mkdir()

        (directory / "SKILL.md").write_text(
            f"---\n"
            f"name: {name}\n"
            f"description: Descripción de {name}.\n"
            f"---\n\n"
            f"{instructions}\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(
        skill_context,
        "SKILLS_DIRECTORY",
        tmp_path,
    )

    return tmp_path


@pytest.mark.parametrize(
    "builder",
    [
        build_design_context,
        build_developer_context,
        build_developer_repair_context,
    ],
)
def test_selected_skill_reaches_agent_context(
    skills_directory,
    builder,
):
    state = MagicMock()

    state.business.model_dump.return_value = {
        "name": "Negocio de prueba",
    }

    state.ux.model_dump.return_value = {
        "sections": [],
    }

    state.available_media = []
    state.website_copy = None
    state.capability_plan = None

    state.website_spec.capabilities = []
    state.website_spec.model_dump_json.return_value = (
        '{"capabilities": []}'
    )

    state.validation.model_dump_json.return_value = (
        '{"is_valid": false, "errors": []}'
    )

    context = builder(state)

    assert "SELECTED_DESIGN_INSTRUCTIONS" in context
    assert "UNSELECTED_REVIEW_INSTRUCTIONS" not in context

    # El catálogo sí incluye la skill que no se ha cargado.
    assert "visual-review" in context

    if builder is build_design_context:
        payload = json.loads(context)
    else:
        skills_text = context.split(
            "SKILLS:",
            maxsplit=1,
        )[1].lstrip()

        skills_payload, _ = json.JSONDecoder().raw_decode(
            skills_text,
        )

        payload = {
            "skills": skills_payload,
        }