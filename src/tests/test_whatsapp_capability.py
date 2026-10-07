from capabilities.implementations.whatsapp import (
    build_whatsapp_implementation,
)


def test_whatsapp_implementation():

    implementation = build_whatsapp_implementation(
        "+34 612 345 678"
    )

    assert implementation.type == "whatsapp"

    assert (
        "https://wa.me/34612345678"
        in implementation.html
    )

    assert (
        'class="capability-whatsapp"'
        in implementation.html
    )