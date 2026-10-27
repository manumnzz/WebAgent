"""Explicit quality/cost profiles. Per-agent overrides always win."""

import os
from agents.agent_config import AgentConfig

CREATIVE_AGENTS = {
    "copy_agent",
    "design_agent",
    "developer_agent",
    "visual_review_agent",
}
PROFILES = {"economy": None, "quality": "gpt-6.1-sol", "studio": "gpt-6-astra"}


def resolve_model(agent: AgentConfig) -> str:
    explicit = os.getenv(f"WEBAGENT_{agent.name.upper()}_MODEL")
    if explicit:
        return explicit
    profile = os.getenv("WEBAGENT_QUALITY_PROFILE", "studio")
    if profile not in PROFILES:
        raise ValueError("WEBAGENT_QUALITY_PROFILE debe ser economy, quality o studio.")
    return (PROFILES[profile] if agent.name in CREATIVE_AGENTS else None) or agent.model


def resolve_reasoning(agent: AgentConfig, model: str) -> dict:
    effort = os.getenv(f"WEBAGENT_{agent.name.upper()}_REASONING")
    if (
        effort is None
        and agent.name in CREATIVE_AGENTS
        and model in {"gpt-6.1-sol", "gpt-6-astra"}
    ):
        effort = "high" if agent.name == "developer_agent" else "medium"
    if effort is not None:
        if effort not in {"none", "low", "medium", "high", "xhigh", "max"}:
            raise ValueError("Nivel de razonamiento no válido.")
        return {"reasoning": {"effort": effort}}
    return {}
