from unittest.mock import MagicMock

from capabilities.capability_resolver import (
    resolve_ready_capability_implementations,
)

from specs.website_spec import (
    WebsiteCapabilitySpec,
)


def test_resolves_only_ready_capabilities():

    ready_whatsapp = MagicMock()

    ready_whatsapp.type = "whatsapp"
    ready_whatsapp.ready = True
    ready_whatsapp.input_values = {
        "whatsapp_number": "+34 612 345 678"
    }

    not_ready_whatsapp = MagicMock()

    not_ready_whatsapp.type = "whatsapp"
    not_ready_whatsapp.ready = False
    not_ready_whatsapp.input_values = {}

    website_spec = MagicMock()

    website_spec.capabilities = [
        ready_whatsapp,
        not_ready_whatsapp,
        WebsiteCapabilitySpec(
            type="gallery",
            required=True,
            reason="Mostrar trabajos del taller.",
            description="Galería",
            required_inputs=[
                "gallery_assets",
            ],
            ready=True,
            missing_inputs=[],
            input_values={
                "gallery_assets": [
                    "assets/car.jpg",
                    "assets/workshop.jpg",
                ]
            },
            developer_requirements=[],
        ),
    ]

    implementations = (
        resolve_ready_capability_implementations(
            website_spec
        )
    )

    whatsapp = next(
        implementation
        for implementation in implementations
        if implementation.type == "whatsapp"
    )

    gallery = next(
        implementation
        for implementation in implementations
        if implementation.type == "gallery"
    )

    assert len(implementations) == 2

    assert (
        "34612345678"
        in whatsapp.html
    )

    assert (
        gallery.html.count("<img")
        == 2
    )