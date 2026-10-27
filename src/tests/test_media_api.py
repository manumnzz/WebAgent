from io import BytesIO
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from intake.api import create_intake_app
from media import api as media_api
from media.storage import load_media_manifest


def build_image():
    output = BytesIO()

    with Image.new("RGB", (120, 80), "red") as image:
        image.save(output, format="PNG")

    return output.getvalue()


@pytest.fixture
def intake(tmp_path):
    client = TestClient(create_intake_app(tmp_path))

    response = client.post(
        "/intake",
        json={
            "business_name": "Negocio de prueba",
            "business_description": "Descripción de prueba.",
        },
    )

    assert response.status_code == 201

    submission_id = response.json()["submission_id"]

    return client, submission_id, tmp_path / submission_id


def test_uploads_logo_and_gallery(intake):
    client, submission_id, directory = intake

    response = client.post(
        f"/intake/{submission_id}/media",
        files=[
            (
                "logo",
                ("../../logo.png", build_image(), "image/png"),
            ),
            (
                "gallery",
                ("foto.png", build_image(), "image/png"),
            ),
        ],
    )

    assert response.status_code == 201

    manifest = load_media_manifest(directory)

    assert [asset.role for asset in manifest.assets] == [
        "logo",
        "gallery",
    ]

    assert response.json() == manifest.model_dump(mode="json")

    for asset in manifest.assets:
        assert (directory / "media" / asset.filename).is_file()

    assert not (directory.parent / "logo.png").exists()


def test_rejects_unknown_submission(intake):
    client, _, _ = intake

    response = client.post(
        f"/intake/{uuid4().hex}/media",
        files={
            "logo": ("logo.png", build_image(), "image/png"),
        },
    )

    assert response.status_code == 404


def test_rejects_invalid_image_without_saving_media(intake):
    client, submission_id, directory = intake

    response = client.post(
        f"/intake/{submission_id}/media",
        files={
            "logo": ("logo.png", b"No es una imagen", "image/png"),
        },
    )

    assert response.status_code == 422
    assert not (directory / "media").exists()


def test_rejects_second_delivery(intake):
    client, submission_id, directory = intake

    url = f"/intake/{submission_id}/media"

    first = client.post(
        url,
        files={
            "logo": ("logo.png", build_image(), "image/png"),
        },
    )

    assert first.status_code == 201
    original = load_media_manifest(directory)

    second = client.post(
        url,
        files={
            "gallery": ("foto.png", build_image(), "image/png"),
        },
    )

    assert second.status_code == 409
    assert load_media_manifest(directory) == original


def test_rejects_oversized_upload(intake, monkeypatch):
    client, submission_id, directory = intake

    monkeypatch.setattr(media_api, "MAX_UPLOAD_BYTES", 8)

    response = client.post(
        f"/intake/{submission_id}/media",
        files={
            "logo": ("logo.png", build_image(), "image/png"),
        },
    )

    assert response.status_code == 413
    assert not (directory / "media").exists()


def test_rejects_empty_delivery(intake):
    client, submission_id, directory = intake

    response = client.post(
        f"/intake/{submission_id}/media",
    )

    assert response.status_code == 422
    assert not (directory / "media").exists()