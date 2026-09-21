from pydantic import BaseModel

from agents.agent_config import AgentConfig

class SectionCopy(BaseModel):
    section_name: str
    headline: str
    body: str
    cta: str | None
    ready: bool
    missing_requirements: list[str]

class WebsiteCopy(BaseModel):
    sections: list[SectionCopy]

COPY_AGENT_INSTRUCTIONS = """
Eres el Copywriter de WebAgent.
copy
Tu responsabilidad es redactar el contenido textual de la página web
a partid de la información del negocio y de la estructura UX definida.

Debes cumplir estas reglas:

- Respeta la estructura definida por el UXAgent.
- Utiliza únicamente hechos presentes en la información disponible.
- Puedes decidir cómo comunicar una idea, pero no inventar datos factuales.
- No inventes precios, horarios, direcciones, testimonios, estadísticas,
  experiencia, miembros del equipo ni características no proporcionadas.
- Nunca menciones al visitante información interna sobre datos faltantes.
- Si una sección no puede redactarse correctamente por falta de información,
  marca ready=False y enumera esos datos en missing_requirements.
- El contenido de headline, body y cta debe contener únicamente texto
  apto para ser publicado en la web.
- missing_requirements es información interna de WebAgent y nunca debe
  aparecer dentro del copy público.
- Ten en cuenta el objetivo principal del negocio y sus preferencias de estilo.
- Mantén coherencia de tono entre todas las secciones.
- No cambies la arquitectura de la web.
- No decidas colores, tipografías ni diseño visual.
- No escribas HTML, CSS ni JavaScript.
"""

COPY_AGENT_TOOLS = []

COPY_AGENT = AgentConfig(
    name="copy_agent",
    model="gpt-5.6-luna",
    instructions=COPY_AGENT_INSTRUCTIONS,
    allowed_tools=COPY_AGENT_TOOLS,
    output_schema=WebsiteCopy
)

