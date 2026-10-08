from agents.agent_config import AgentConfig
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    address: str | None = None
class BusinessProfile(BaseModel):
    name: str | None
    business_type: str
    location: str | None
    services: list[str]
    main_goal: str | None
    desired_style: list[str]
    
    requested_features: list[str] = Field(
        default_factory=list
    )

    contact: ContactInfo = Field(
        default_factory=ContactInfo
    )


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
- Conserva las funcionalidades, canales, contenidos o características
  de la web que el usuario solicite explícitamente en requested_features.

- requested_features describe lo que pide el usuario; no selecciones
  capabilities ni tomes decisiones técnicas.

- Extrae en contact únicamente datos de contacto proporcionados
  explícitamente o encontrados mediante una fuente disponible:
  teléfono, WhatsApp, email y dirección.

- No inventes ningún dato de contacto.

- Si desconoces un dato de contacto, déjalo como null.
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