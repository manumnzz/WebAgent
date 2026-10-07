from urllib.parse import quote_plus

from capabilities.capability_implementation import (
    CapabilityImplementation,
)

def build_maps_implementation(
        business_address: str,
) -> CapabilityImplementation:

    clean_address = business_address.strip()

    if not clean_address:
        raise ValueError(
            "La dirección del negocio no es válida."
        )

    encoded_address = quote_plus(
        clean_address
    )

    maps_url = (
        "https://www.google.com/maps/search/"
        f"?api=1&query={encoded_address}"
    )

    html = f"""
<a
    href="{maps_url}"
    class="capability-maps"
    target="_blank"
    rel="noopener noreferrer"
>
    Ver ubicación en Google Maps
</a>
""".strip()

    return CapabilityImplementation(
        type="maps",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            "Ubicación integrada mediante Google Maps."
        ],
    )