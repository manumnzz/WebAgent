from capabilities.implementations.maps import (
    build_maps_implementation,
)


def test_maps_implementation():

    implementation = build_maps_implementation(
        "Calle Sierpes 15, Sevilla"
    )

    assert implementation.type == "maps"

    assert (
        "https://www.google.com/maps/search/"
        in implementation.html
    )

    assert (
        "Calle+Sierpes+15%2C+Sevilla"
        in implementation.html
    )

    assert (
        'class="capability-maps"'
        in implementation.html
    )