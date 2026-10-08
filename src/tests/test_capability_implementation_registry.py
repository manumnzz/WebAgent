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

def test_get_contact_form_builder():

    builder = get_capability_implementation_builder(
        "contact_form"
    )

    implementation = builder(
        contact_destination="contacto@irongarage.es"
    )

    assert implementation.type == "contact_form"

    assert (
        "contacto@irongarage.es"
        in implementation.html
    )

def test_get_gallery_builder():

    builder = get_capability_implementation_builder(
        "gallery"
    )

    implementation = builder(
        gallery_assets=[
            "assets/car.jpg",
            "assets/workshop.jpg",
        ]
    )

    assert implementation.type == "gallery"

    assert (
        implementation.html.count("<img")
        == 2
    )

def test_get_reviews_builder():

    builder = get_capability_implementation_builder(
        "reviews"
    )

    implementation = builder(
        review_data=[
            {
                "author": "Carlos",
                "text": "Trabajo excelente.",
                "rating": 5,
            }
        ]
    )

    assert implementation.type == "reviews"
    assert "Carlos" in implementation.html