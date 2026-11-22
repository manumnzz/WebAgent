
import pytest

from agents.model_config import (
    AGENT_MODELS,
    DEFAULT_MODEL,
    get_agent_model,
)


def test_all_agents_have_a_configured_model():
    expected_agents = {
        "business_agent",
        "ux_agent",
        "copy_agent",
        "design_agent",
        "developer_agent",
    }

    assert set(AGENT_MODELS) == expected_agents


def test_models_have_valid_values():
    for model in AGENT_MODELS.values():
        assert isinstance(model, str)
        assert model.strip()


def test_default_model():
    assert DEFAULT_MODEL == "gpt-5.6-luna"


def test_get_agent_model():
    for name, model in AGENT_MODELS.items():
        assert get_agent_model(name) == model


def test_unknown_agent_raises_error():
    with pytest.raises(ValueError, match="Agente desconocido"):
        get_agent_model("unknown_agent")

def test_environment_variable_overrides_model(monkeypatch):
    import importlib
    import agents.model_config as model_config

    monkeypatch.setenv("UX_AGENT_MODEL", "test-model")
    importlib.reload(model_config)

    try:
        assert model_config.get_agent_model("ux_agent") == "test-model"

        assert (
            model_config.get_agent_model("developer_agent")
            == model_config.DEFAULT_MODEL
        )
    finally:
        monkeypatch.delenv("UX_AGENT_MODEL", raising=False)
        importlib.reload(model_config)