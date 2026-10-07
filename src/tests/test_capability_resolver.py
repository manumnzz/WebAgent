from unittest.mock import MagicMock

from capabilities.capability_resolver import (
    resolve_ready_capability_implementations,
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
    ]

    implementations = (
        resolve_ready_capability_implementations(
            website_spec
        )
    )

    assert len(implementations) == 1

    assert implementations[0].type == "whatsapp"

    assert (
        "34612345678"
        in implementations[0].html
    )