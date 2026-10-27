from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image
from pydantic import ValidationError

from media.image_processing import InvalidMediaError
from media.storage import (
    MediaAlreadyExistsError,
    MediaUpload,
    load_media_manifest,
    save_media_batch,
)


def build_image():
    output = BytesIO()

    with Image.new("RGB", (120, 80), "red") as image:
        image.save(output, format="PNG")

    return output.getvalue()


@pytest.fixture
def submission_directory(tmp_path):
    directory = tmp_path / "encargo"
    directory.mkdir()

    (directory / "project_input.json").write_text(
        "{}",
        encoding="utf-8",
    )

    return directory


def test_saves_images_and_manifest(submission_directory):
    manifest = save_media_batch(
        submission_directory,
        [
            MediaUpload(build_image(), role="logo"),
            MediaUpload(build_image(), role="gallery"),
        ],
    )

    assert load_media_manifest(submission_directory) == manifest

    for asset in manifest.assets:
        image_path = (
            submission_directory / "media" / asset.filename
        )

        assert image_path.stat().st_size == asset.size_bytes

        with Image.open(image_path) as image:
            assert image.format == "WEBP"
            assert image.size == (asset.width, asset.height)


def test_invalid_second_image_leaves_no_media(
    submission_directory,
):
    with pytest.raises(InvalidMediaError):
        save_media_batch(
            submission_directory,
            [
                MediaUpload(build_image(), role="gallery"),
                MediaUpload(b"No es una imagen", role="gallery"),
            ],
        )

    assert not (submission_directory / "media").exists()
    assert list(submission_directory.glob(".media-*")) == []


def test_rejects_two_logos_without_leaving_media(
    submission_directory,
):
    with pytest.raises(ValidationError):
        save_media_batch(
            submission_directory,
            [
                MediaUpload(build_image(), role="logo"),
                MediaUpload(build_image(), role="logo"),
            ],
        )

    assert not (submission_directory / "media").exists()
    assert list(submission_directory.glob(".media-*")) == []


def test_existing_delivery_is_not_overwritten(
    submission_directory,
):
    original = save_media_batch(
        submission_directory,
        [MediaUpload(build_image(), role="gallery")],
    )

    with pytest.raises(MediaAlreadyExistsError):
        save_media_batch(
            submission_directory,
            [MediaUpload(build_image(), role="logo")],
        )

    assert load_media_manifest(submission_directory) == original


def test_manifest_write_failure_leaves_no_media(
    submission_directory,
    monkeypatch,
):
    original_write_text = Path.write_text

    def fail_manifest_write(path, *args, **kwargs):
        if path.name == "media.json":
            raise OSError("Fallo de escritura simulado")

        return original_write_text(path, *args, **kwargs)

    monkeypatch.setattr(
        Path,
        "write_text",
        fail_manifest_write,
    )

    with pytest.raises(OSError):
        save_media_batch(
            submission_directory,
            [MediaUpload(build_image(), role="gallery")],
        )

    assert not (submission_directory / "media").exists()
    assert list(submission_directory.glob(".media-*")) == []


def test_requires_existing_submission(tmp_path):
    with pytest.raises(FileNotFoundError):
        save_media_batch(
            tmp_path / "inexistente",
            [MediaUpload(build_image(), role="gallery")],
        )