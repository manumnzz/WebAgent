import re

from capabilities.capability_implementation import (
    CapabilityImplementation,
)

def build_whatsapp_implementation(
        whatsapp_number: str,
) -> CapabilityImplementation:

    clean_number = re.sub(
        r"\D",
        "",
        whatsapp_number
    )

    if not clean_number:
        raise ValueError(
            "El número de WhatsApp no es válido."
        )

    html = f"""
    <a
        href="https://wa.me/{clean_number}"
        class="capability-whatsapp"
        target="_blank"
        rel="noopener noreferrer"
    >
        Contactar por WhatsApp
    </a>
    """.strip()

    return CapabilityImplementation(
        type="whatsapp",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            "WhatsApp integrado mediante wa.me."
        ],
    )