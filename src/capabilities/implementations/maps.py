from html import escape
from urllib.parse import quote_plus

from capabilities.capability_implementation import CapabilityImplementation


def build_maps_implementation(
    business_address: str,
) -> CapabilityImplementation:
    clean_address = business_address.strip()
    if not clean_address:
        raise ValueError("La dirección del negocio no es válida.")

    encoded_address = quote_plus(clean_address)
    map_url = escape(
        f"https://www.google.com/maps?q={encoded_address}&output=embed",
        quote=True,
    )
    link_url = escape(
        f"https://www.google.com/maps/search/?api=1&query={encoded_address}",
        quote=True,
    )
    frame_attributes = f'src="{map_url}"'
    link_attributes = f'href="{link_url}"'

    html = f"""
<div class="capability-maps-block">
    <iframe
        class="capability-maps-frame"
        title="Ubicación del negocio en Google Maps"
        width="400"
        height="400"
        loading="lazy"
        referrerpolicy="strict-origin-when-cross-origin"
        {frame_attributes}
    ></iframe>
    <a
        {link_attributes}
        class="capability-maps"
        target="_blank"
        rel="noopener noreferrer"
    >
        Ver ubicación en Google Maps
    </a>
</div>
""".strip()

    return CapabilityImplementation(
        type="maps",
        html=html,
        css="""
.capability-maps-frame {
    display: block;
    width: 100%;
    max-width: 400px;
    height: auto;
    aspect-ratio: 1;
    border: 0;
}
""".strip(),
        javascript="",
        implementation_notes=[
            "Mapa cuadrado incrustado con enlace para abrir la ubicación en Google Maps.",
        ],
    )
