import pytest
from agents.agent_config import AgentConfig
from agents.model_policy import resolve_model, resolve_reasoning


@pytest.fixture
def creative(monkeypatch):
    for key in (
        "WEBAGENT_QUALITY_PROFILE",
        "WEBAGENT_DESIGN_AGENT_MODEL",
        "WEBAGENT_DESIGN_AGENT_REASONING",
    ):
        monkeypatch.delenv(key, raising=False)
    return AgentConfig("design_agent", "gpt-5.6-luna", "", [], dict)


def test_studio_default_and_economy_escape_hatch(creative, monkeypatch):
    assert resolve_model(creative) == "gpt-6-astra"
    monkeypatch.setenv("WEBAGENT_QUALITY_PROFILE", "economy")
    assert resolve_model(creative) == "gpt-5.6-luna"


def test_studio_and_explicit_override(creative, monkeypatch):
    monkeypatch.setenv("WEBAGENT_QUALITY_PROFILE", "studio")
    assert resolve_model(creative) == "gpt-6-astra"
    monkeypatch.setenv("WEBAGENT_DESIGN_AGENT_MODEL", "custom-model")
    assert resolve_model(creative) == "custom-model"
    assert resolve_reasoning(creative, "custom-model") == {}


def test_business_model_is_not_changed(creative, monkeypatch):
    creative.name = "business_agent"
    monkeypatch.setenv("WEBAGENT_QUALITY_PROFILE", "studio")
    assert resolve_model(creative) == "gpt-5.6-luna"


def test_reasoning_override(creative, monkeypatch):
    assert resolve_reasoning(creative, "gpt-6.1-sol") == {
        "reasoning": {"effort": "medium"}
    }
    monkeypatch.setenv("WEBAGENT_DESIGN_AGENT_REASONING", "medium")
    assert resolve_reasoning(creative, "gpt-6.1-sol") == {
        "reasoning": {"effort": "medium"}
    }


def test_invalid_profile_fails_early(creative, monkeypatch):
    monkeypatch.setenv("WEBAGENT_QUALITY_PROFILE", "unknown")
    with pytest.raises(ValueError):
        resolve_model(creative)
