from agents.agent_config import AgentConfig
from pydantic import BaseModel

class BusinessProfile(BaseModel):
    name: str | None
    business_type: str
    location: str | None
    services: list[str]
    main_goal: str | None
    desired_style: list[str]


BUSINESS_AGENT_INSTRUCTIONS = """
Eres el Business Analyst de WebAgent.

Tu responsabilidad es analizar la descripción proporcionada
sobre un negocio y extraer la información relevante para
la futura creación de su página web.

Debes cumplir estas reglas:

- No inventes información.
- Diferencia claramente información explícita de suposiciones.
- Si desconoces un dato, indícalo.
- No diseñes la web.
- No escribas código.
- No generes el copy final de la página.
"""


BUSINESS_AGENT_TOOLS = [
    "search_business",
    "search_business_preferences"
]

BUSINESS_AGENT = AgentConfig(
    name="business_agent",
    model="gpt-5.6-luna",
    instructions=BUSINESS_AGENT_INSTRUCTIONS,
    allowed_tools=BUSINESS_AGENT_TOOLS,
    output_schema=BusinessProfile
)