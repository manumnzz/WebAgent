from html import escape

from capabilities.capability_implementation import (
    CapabilityImplementation
)

def build_gallery_implementation(
        gallery_assets: list[str],
) -> CapabilityImplementation:

    clean_assets = [
        asset.strip()
        for asset in gallery_assets
        if asset.strip()
    ]

    if not clean_assets:
        raise ValueError(
            "La galería no contiene recursos válidos."
        )

    gallery_items = []

    for index, asset in enumerate(
        clean_assets,
        start=1,
    ):

        safe_asset = escape(
            asset,
            quote=True,
        )

        gallery_items.append(
            f"""
            <figure class="capability-gallery-item">
                <img
                    src="{safe_asset}"
                    alt="Imagen de galería {index}"
                    loading="lazy"
                >
            </figure>
            """.strip()
        )

    items_html = "\n".join(
        gallery_items
    )

    html = f"""
<div class="capability-gallery">
    {items_html}
</div>
""".strip()

    return CapabilityImplementation(
        type="gallery",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            (
                f"Galería integrada con "
                f"{len(clean_assets)} recurso(s) visual(es)."
            )
        ],
    )