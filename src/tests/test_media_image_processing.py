from io import BytesIO

import pytest
from PIL import Image

from media import image_processing
from media.image_processing import (
    InvalidMediaError,
    prepare_image,
)


def build_image_bytes(
    *,
    image_format="JPEG",
    size=(120, 80),
    mode="RGB",
    color="red",
):
    output = BytesIO()

    with Image.new(mode, size, color) as image:
        image.save(output, format=image_format)

    return output.getvalue()


def test_prepares_large_image_without_distorting_it():
    content = build_image_bytes(size=(3000, 1500))

    asset, prepared = prepare_image(
        content,
        role="gallery",
    )

    assert asset.width == 2400
    assert asset.height == 1200
    assert asset.size_bytes == len(prepared)

    with Image.open(BytesIO(prepared)) as image:
        assert image.format == "WEBP"
        assert image.size == (2400, 1200)


def test_preserves_logo_transparency():
    content = build_image_bytes(
        image_format="PNG",
        mode="RGBA",
        color=(255, 0, 0, 0),
    )

    asset, prepared = prepare_image(
        content,
        role="logo",
    )

    assert asset.role == "logo"

    with Image.open(BytesIO(prepared)) as image:
        assert image.convert("RGBA").getpixel((0, 0))[3] == 0


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"Esto no es una imagen",
        b"\xff\xd8\xff",
    ],
)
def test_rejects_invalid_images(content):
    with pytest.raises(InvalidMediaError):
        prepare_image(content, role="gallery")


def test_rejects_unsupported_format():
    content = build_image_bytes(image_format="GIF")

    with pytest.raises(InvalidMediaError):
        prepare_image(content, role="gallery")


def test_rejects_upload_over_size_limit(monkeypatch):
    content = build_image_bytes()

    monkeypatch.setattr(
        image_processing,
        "MAX_UPLOAD_BYTES",
        len(content) - 1,
    )

    with pytest.raises(InvalidMediaError):
        prepare_image(content, role="gallery")


def test_rejects_image_over_pixel_limit(monkeypatch):
    content = build_image_bytes(size=(120, 80))

    monkeypatch.setattr(
        image_processing,
        "MAX_IMAGE_PIXELS",
        100,
    )

    with pytest.raises(InvalidMediaError):
        prepare_image(content, role="gallery")