from capabilities.implementation_registry import (
    get_capability_implementation_builder,
    build_capability_implementation,
)


def test_get_whatsapp_builder():

    builder = get_capability_implementation_builder(
        "whatsapp"
    )

    implementation = builder(
        whatsapp_number="+34 612 345 678"
    )

    assert implementation.type == "whatsapp"

    assert (
        "https://wa.me/34612345678"
        in implementation.html
    )


def test_build_whatsapp_from_input_values():

    implementation = build_capability_implementation(
        capability_type="whatsapp",
        input_values={
            "whatsapp_number": "+34 612 345 678"
        }
    )

    assert implementation.type == "whatsapp"

    assert (
        "34612345678"
        in implementation.html
    )

def test_build_maps_from_input_values():

    implementation = build_capability_implementation(
        capability_type="maps",
        input_values={
            "business_address":
                "Calle Sierpes 15, Sevilla"
        }
    )

    assert implementation.type == "maps"

    assert (
        "Calle+Sierpes+15%2C+Sevilla"
        in implementation.html
    )