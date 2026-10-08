import pytest

from capabilities.implementations.gallery import (
    build_gallery_implementation,
)


def test_gallery_capability():

    implementation = build_gallery_implementation(
        gallery_assets=[
            "assets/garage-front.jpg",
            "assets/bmw-e46.jpg",
            "assets/workshop.jpg",
        ]
    )

    assert implementation.type == "gallery"

    assert (
        'src="assets/garage-front.jpg"'
        in implementation.html
    )

    assert (
        'src="assets/bmw-e46.jpg"'
        in implementation.html
    )

    assert (
        'src="assets/workshop.jpg"'
        in implementation.html
    )

    assert (
        implementation.html.count("<img")
        == 3
    )

    assert 'loading="lazy"' in implementation.html


def test_gallery_rejects_empty_assets():

    with pytest.raises(ValueError):

        build_gallery_implementation(
            gallery_assets=[]
        )


def test_gallery_ignores_empty_assets():

    implementation = build_gallery_implementation(
        gallery_assets=[
            "assets/car.jpg",
            "   ",
        ]
    )

    assert (
        implementation.html.count("<img")
        == 1
    )