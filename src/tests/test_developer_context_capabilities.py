from unittest.mock import MagicMock

from context.context_builders import (
    build_developer_context,
)


def test_developer_context_contains_prebuilt_capability():

    whatsapp = MagicMock()

    whatsapp.type = "whatsapp"
    whatsapp.ready = True
    whatsapp.input_values = {
        "whatsapp_number": "+34 612 345 678"
    }

    website_spec = MagicMock()

    website_spec.capabilities = [
        whatsapp
    ]

    website_spec.model_dump_json.return_value = (
        '{"test": "website_spec"}'
    )

    state = MagicMock()
    state.website_spec = website_spec

    context = build_developer_context(
        state
    )

    assert (
        "PREBUILT_CAPABILITY_IMPLEMENTATIONS"
        in context
    )

    assert (
        "https://wa.me/34612345678"
        in context
    )

    assert (
        "capability-whatsapp"
        in context
    )

    assert "WEBSITE_CONTENT_RUNTIME" not in context
    assert "data-content" not in context
    assert '{"test": "website_spec"}' in context
