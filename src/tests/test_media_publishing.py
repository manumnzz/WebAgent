from io import BytesIO

import pytest
from PIL import Image

from media.publishing import publish_submission_media
from media.storage import MediaUpload, save_media_batch
from projects.workspace import build_project_workspace


@pytest.fixture
def submission(tmp_path):
    directory = tmp_path / "intake"
    directory.mkdir()

    (directory / "project_input.json").write_text(
        "{}",
        encoding="utf-8",
    )

    output = BytesIO()

    with Image.new("RGB", (120, 80), "red") as image:
        image.save(output, format="PNG")

    manifest = save_media_batch(
        directory,
        [
            MediaUpload(output.getvalue(), role="logo"),
            MediaUpload(output.getvalue(), role="gallery"),
        ],
    )

    return directory, manifest


def test_publishes_images_without_publishing_manifest(
    submission,
    tmp_path,
):
    directory, manifest = submission

    workspace = build_project_workspace(
        "fisio",
        projects_directory=tmp_path / "projects",
    )

    published = publish_submission_media(directory, workspace)

    assert len(published) == 2

    for original, asset in zip(manifest.assets, published):
        source = directory / "media" / original.filename
        destination = workspace.website_directory / asset.path

        assert destination.read_bytes() == source.read_bytes()
        assert asset.id == original.id
        assert asset.role == original.role

    assert not (
        workspace.website_directory / "assets" / "media.json"
    ).exists()


def test_missing_image_does_not_publish_partial_assets(
    submission,
    tmp_path,
):
    directory, manifest = submission

    (directory / "media" / manifest.assets[-1].filename).unlink()

    workspace = build_project_workspace(
        "fisio",
        projects_directory=tmp_path / "projects",
    )

    with pytest.raises(FileNotFoundError):
        publish_submission_media(directory, workspace)

    assert not (
        workspace.website_directory / "assets"
    ).exists()


def test_submission_without_media_returns_empty_list(tmp_path):
    directory = tmp_path / "intake"
    directory.mkdir()

    workspace = build_project_workspace(
        "sin-imagenes",
        projects_directory=tmp_path / "projects",
    )

    assert publish_submission_media(directory, workspace) == []