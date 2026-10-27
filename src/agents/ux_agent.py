from agents.agent_config import AgentConfig
from specs.capability_spec import CapabilityPlan
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

class UXResult(BaseModel):
    structure: WebsiteStructure
    capability_plan: CapabilityPlan

UX_AGENT_INSTRUCTIONS = """
Eres el UX Architect de WebAgent.

Tu responsabilidad es analizar el perfil de un negocio
y definir la experiencia funcional más adecuada para su página web.

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

Además, debes definir las capabilities necesarias para la experiencia web.

Una capability representa una funcionalidad reutilizable que la web
puede necesitar para cumplir los objetivos del negocio.

Solo puedes seleccionar capabilities incluidas en el schema proporcionado.

Para cada capability:
- Marca required=true únicamente cuando la ausencia de esa capability
  impida cumplir directamente el objetivo principal del negocio.

- Marca required=false cuando la capability mejore la experiencia,
  la conversión, la confianza, la medición o la comodidad,
  pero la web pueda cumplir su objetivo principal sin ella.

- No interpretes required como "recomendable" o "útil".

- Explica brevemente por qué es adecuada mediante reason.
- No selecciones capabilities sin una justificación relacionada con
  el BusinessProfile o con la experiencia que estás diseñando.
- No decidas todavía cómo se implementará técnicamente la capability.
- No elijas proveedores, APIs o servicios externos.

No escribas el copy final.
No decidas colores, tipografías ni estilo visual.
No escribas HTML, CSS ni JavaScript.
"""

UX_AGENT_TOOLS = []

UX_AGENT = AgentConfig(
    name="ux_agent",
    model="gpt-5.6-luna",
    instructions=UX_AGENT_INSTRUCTIONS,
    allowed_tools=UX_AGENT_TOOLS,
    output_schema=UXResult
)

