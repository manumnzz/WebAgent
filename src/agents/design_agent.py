from pydantic import BaseModel

from agents.agent_config import AgentConfig

class SectionDesign(BaseModel):
    section_name: str
    layout: str
    visual_notes: str
    required_inputs: list[str]

class DesignSpec(BaseModel):
    visual_direction: str
    color_palette: list[str]
    typography_direction: str
    section_designs: list[SectionDesign]

    missing_assets: list[str]
    missing_information: list[str]

DESIGN_AGENT_INSTRUCTIONS = """
Eres el Visual Designer de WebAgent.

Tu responsabilidad es definir la dirección visual de la página web
a partir de la información del negocio y de la estructura UX.

Debes cumplir estas reglas:

- Respeta la estructura definida por el UXAgent.
- Utiliza desired_style únicamente como preferencia visual para la web.
- Puedes proponer colores, composición, jerarquía, layouts y dirección tipográfica.
- No interpretes las preferencias visuales como hechos sobre el negocio.
- No inventes logotipos, fotografías, testimonios ni activos que no existan.
- Si el diseño necesita imágenes u otros recursos no disponibles,
  indícalos en required_assets y missing_assets.
- No cambies los servicios ni la información factual del negocio.
- No escribas el copy de la página.
- No escribas HTML, CSS ni JavaScript.
"""

DESIGN_AGENT_TOOLS = []

DESIGN_AGENT = AgentConfig(
    name="design_agent",
    model="gpt-5.6-luna",
    instructions=DESIGN_AGENT_INSTRUCTIONS,
    allowed_tools=DESIGN_AGENT_TOOLS,
    output_schema=DesignSpec
)

