"""Regressions for removing the visual experiment while retaining project tools."""

import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

from agents.agent_config import AgentConfig
from agents.business_agent import BusinessProfile
from agents.copy_agent import WebsiteCopy
from agents.design_agent import DesignSpec
from agents.developer_agent import DevelopmentResult
from agents.ux_agent import WebsiteStructure
from context.context_builders import (
    build_copy_context,
    build_design_context,
    build_developer_context,
    build_developer_repair_context,
)
from specs.capability_spec import CapabilityPlan, CapabilitySpec
from specs.storage import load_website_spec
from specs.website_spec_builder import build_website_spec
from state.project_state import ProjectState
from validation.models import ValidationResult


@pytest.fixture
def classic_state():
    state = ProjectState(
        business=BusinessProfile(
            name="Taller", business_type="taller", location="Sevilla",
            services=[], main_goal=None, desired_style=[],
        ),
        ux=WebsiteStructure(
            sections=[], navigation=[], primary_cta=None, missing_content=[],
        ),
        capability_plan=CapabilityPlan(capabilities=[]),
        website_copy=WebsiteCopy(sections=[]),
        design=DesignSpec(
            visual_direction="Fotografía protagonista",
            color_palette=["#123456"], typography_direction="Legible",
            section_designs=[], missing_assets=[], missing_information=[],
        ),
        validation=ValidationResult(is_valid=True, errors=[]),
    )
    state.website_spec = build_website_spec(state)
    return state


@pytest.mark.parametrize("builder", [
    build_design_context, build_developer_context, build_developer_repair_context,
])
def test_classic_contexts_do_not_inject_visual_experiment(classic_state, builder):
    context = builder(classic_state)
    for removed in ("SKILLS:", '"skills"', '"design_system"', '"art_direction"'):
        assert removed not in context
    if builder is build_design_context:
        assert set(json.loads(context)) == {"business", "ux", "available_media"}
    else:
        assert '"color_palette": [' in context
        assert "#123456" in context
    if builder is build_developer_repair_context:
        assert "VALIDATION_RESULT:" in context


def test_legacy_visual_contracts_load_without_reinjecting_visual_fields(
    tmp_path, classic_state,
):
    payload = classic_state.website_spec.model_dump(mode="json")
    payload.update({
        "design_system": {"colors": {"accent": "#D97706"}},
        "art_direction": {"concept": "Previous experiment"},
    })
    path = tmp_path / "website_spec.json"
    path.write_text(json.dumps({"schema_version": 1, "website_spec": payload}))
    restored = load_website_spec(path)
    assert restored.color_palette == ["#123456"]
    assert restored.visual_direction == "Fotografía protagonista"
    assert "design_system" not in restored.model_dump()
    assert "art_direction" not in restored.model_dump()
    assert "design_system" in json.loads(path.read_text())["website_spec"]


def test_copy_retains_functional_readiness_context(classic_state):
    classic_state.website_spec = None
    classic_state.capability_plan = CapabilityPlan(capabilities=[
        CapabilitySpec(type="contact_form", required=False, reason="Contacto"),
    ])
    constraints = json.loads(build_copy_context(classic_state))["capability_constraints"]
    assert constraints[0]["type"] == "contact_form"
    assert constraints[0]["ready"] is False


def test_runner_uses_configured_model_without_studio_override(monkeypatch):
    from agents import agent_runner

    expected = DevelopmentResult(
        files_created=[], files_modified=[], implementation_notes=[],
    )
    response = Mock(output=[], output_parsed=expected)
    client = Mock()
    client.responses.parse.return_value = response
    monkeypatch.setattr(agent_runner, "OpenAI", Mock(return_value=client))
    monkeypatch.setenv("WEBAGENT_QUALITY_PROFILE", "studio")
    monkeypatch.setenv("WEBAGENT_DEVELOPER_AGENT_MODEL", "unwanted-override")
    agent = AgentConfig(
        name="developer_agent", model="configured-model", instructions="Instructions",
        allowed_tools=[], output_schema=DevelopmentResult,
    )
    assert agent_runner.run_agent(agent, "Input") is expected
    arguments = client.responses.parse.call_args.kwargs
    assert arguments["model"] == "configured-model"
    assert "reasoning" not in arguments
    assert arguments["input"][1]["content"] == "Input"


def test_generation_cli_has_no_visual_review_dependency():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "src/main.py", "--help"], cwd=root,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "--project-id" in result.stdout
    assert "--visual-review" not in result.stdout


def test_development_help_keeps_repair_without_visual_commands():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/dev.py", "ayuda"], cwd=root,
        capture_output=True, text=True, check=True,
    )
    for command in ("formulario", "generar", "web", "reparar", "test"):
        assert f"make {command}" in result.stdout
    assert "make capturas" not in result.stdout
    assert "make mejorar" not in result.stdout
