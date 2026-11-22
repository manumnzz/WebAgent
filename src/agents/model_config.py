import os

DEFAULT_MODEL = "gpt-5.6-luna"

AGENT_MODELS = {
    "business_agent": os.getenv("BUSINESS_AGENT_MODEL", DEFAULT_MODEL),
    "ux_agent": os.getenv("UX_AGENT_MODEL", DEFAULT_MODEL),
    "copy_agent": os.getenv("COPY_AGENT_MODEL", DEFAULT_MODEL),
    "design_agent": os.getenv("DESIGN_AGENT_MODEL", DEFAULT_MODEL),
    "developer_agent": os.getenv("DEVELOPER_AGENT_MODEL", DEFAULT_MODEL),
}


def get_agent_model(agent_name: str) -> str:
    if agent_name not in AGENT_MODELS:
        raise ValueError(f"Agente desconocido: {agent_name}")

    return AGENT_MODELS[agent_name]