from agents.agent_config import AgentConfig
from pydantic import BaseModel


class SectionSpec(BaseModel):
    name: str
    purpose: str
    required_content: list[str]

class WebsiteStructure(BaseModel):
    sections: list[SectionSpec]
    navigation: list[str]
    primary_cta: str | None
    missing_content: list[str]

UX_AGENT_INSTRUCTIONS = """
Eres el UX Architect de WebAgent.

Tu responsabilidad es analizar el perfil de un negocio
y definir la estructura funcional más adecuada para su página web.

Debes cumplir estas reglas:

- Utiliza el BusinessProfile como fuente de información sobre el negocio.
- Puedes proponer secciones que consideres útiles para cumplir el objetivo de la web.
- Proponer una sección no significa asumir que su contenido existe.
- Si una sección necesita información o materiales no presentes en el BusinessProfile,
  debes indicarlos en missing_content.
- No inventes testimonios, fotografías, datos de contacto,
  precios, miembros del equipo ni ninguna información factual.
- Define el propósito de cada sección.
- Define los elementos principales de navegación.
- Identifica la acción principal de la página.
- No escribas el copy final.
- No decidas colores, tipografías ni estilo visual.
- No escribas HTML, CSS ni JavaScript.
"""

UX_AGENT_TOOLS = []

UX_AGENT = AgentConfig(
    name="ux_agent",
    model="gpt-5.6-luna",
    instructions=UX_AGENT_INSTRUCTIONS,
    allowed_tools=UX_AGENT_TOOLS,
    output_schema=WebsiteStructure
)

