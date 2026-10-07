from pydantic import BaseModel

from specs.capability_spec import CapabilityType
from state.project_state import CapabilityPlan

class CapabilityDefinition(BaseModel):
    type: CapabilityType
    description: str
    required_inputs: list[str]
    developer_requirements: list[str]

CAPABILITY_REGISTRY: dict[CapabilityType, CapabilityDefinition] = {
    "booking": CapabilityDefinition(
        type="booking",
        description="Permite al visitante iniciar o completar una reserva.",
        required_inputs=[
            "booking_configuration",
        ],
        developer_requirements=[
            "Debe existir una llamada a la acción clara para reservar.",
            "No se deben inventar URLs, proveedores ni datos de reserva.",
            "La acción de reserva debe ser fácilmente accesible.",
        ],
    ),

    "contact_form": CapabilityDefinition(
        type="contact_form",
        description="Permite al visitante contactar con el negocio mediante un formulario.",
        required_inputs=[
            "contact_destination",
        ],
        developer_requirements=[
            "El formulario debe solicitar únicamente información necesaria.",
            "Debe existir una acción de envío claramente identificable.",
            "No se debe simular un envío funcional si no existe backend o proveedor configurado.",
        ],
    ),

    "whatsapp": CapabilityDefinition(
        type="whatsapp",
        description="Permite iniciar una conversación con el negocio mediante WhatsApp.",
        required_inputs=[
            "whatsapp_number",
        ],
        developer_requirements=[
            "Debe existir una acción visible para iniciar la conversación.",
            "No se debe inventar un número de teléfono.",
        ],
    ),

    "maps": CapabilityDefinition(
        type="maps",
        description="Permite mostrar o enlazar la ubicación física del negocio.",
        required_inputs=[
            "business_address",
        ],
        developer_requirements=[
            "La ubicación mostrada debe corresponder a la dirección real del negocio.",
            "No se deben inventar coordenadas ni direcciones.",
        ],
    ),

    "gallery": CapabilityDefinition(
        type="gallery",
        description="Permite mostrar contenido visual real del negocio o de sus trabajos.",
        required_inputs=[
            "gallery_assets",
        ],
        developer_requirements=[
            "La galería debe utilizar recursos visuales disponibles.",
            "No debe inventar fotografías del negocio como si fueran reales.",
            "Las imágenes deben integrarse de forma coherente con la estructura de la web.",
        ],
    ),

    "reviews": CapabilityDefinition(
        type="reviews",
        description="Permite mostrar opiniones o valoraciones reales sobre el negocio.",
        required_inputs=[
            "review_data",
        ],
        developer_requirements=[
            "No se deben inventar reseñas ni valoraciones.",
            "Las opiniones mostradas deben proceder de datos proporcionados o de una fuente configurada.",
        ],
    ),

    "analytics": CapabilityDefinition(
        type="analytics",
        description="Permite medir el comportamiento y las conversiones de la web.",
        required_inputs=[
            "analytics_configuration",
        ],
        developer_requirements=[
            "No se deben inventar identificadores de servicios de analítica.",
            "La integración debe utilizar únicamente una configuración proporcionada.",
        ],
    ),
}

def get_capability_definition(
        capability_type: CapabilityType,
) -> CapabilityDefinition:
    return CAPABILITY_REGISTRY[capability_type]

def resolve_capability_plan(
    plan: CapabilityPlan,
) -> list[CapabilityDefinition]:
    return [
        get_capability_definition(capability.type)
        for capability in plan.capabilities
    ]