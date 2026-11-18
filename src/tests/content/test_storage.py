
import pytest

from pydantic import ValidationError

from content.models import (
    WebsiteContent,
    ServiceContent,
)

from content.storage import (
    save_website_content,
    load_website_content,
)

from projects.workspace import build_project_workspace


@pytest.fixture
def sample_content():
    return WebsiteContent(
        business_name="Iron Garage",
        services=[
            ServiceContent(
                id="diagnostico",
                name="Diagnóstico electrónico",
                price=None,
            )
        ],
    )


def test_save_creates_content_file(
    tmp_path,
    sample_content,
):
    path = tmp_path / "website" / "content.json"

    save_website_content(sample_content, path)

    assert path.is_file()


def test_load_restores_original_content(
    tmp_path,
    sample_content,
):
    path = tmp_path / "content.json"

    save_website_content(sample_content, path)

    restored = load_website_content(path)

    assert restored == sample_content


def test_storage_preserves_utf8(
    tmp_path,
    sample_content,
):
    path = tmp_path / "content.json"

    save_website_content(sample_content, path)

    raw = path.read_text(encoding="utf-8")

    assert "Diagnóstico electrónico" in raw


def test_storage_can_update_existing_content(
    tmp_path,
    sample_content,
):
    path = tmp_path / "content.json"

    save_website_content(sample_content, path)

    sample_content.services[0].price = "40 €"

    save_website_content(sample_content, path)

    restored = load_website_content(path)

    assert restored.services[0].price == "40 €"


def test_load_rejects_invalid_json(tmp_path):
    path = tmp_path / "content.json"

    path.write_text(
        '{"business_name":',
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_website_content(path)


def test_load_rejects_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_website_content(path)


def test_projects_have_independent_content(
    tmp_path,
):
    iron = build_project_workspace(
        "iron-garage",
        projects_directory=tmp_path,
    )

    fisio = build_project_workspace(
        "fisio-alameda",
        projects_directory=tmp_path,
    )

    save_website_content(
        WebsiteContent(business_name="Iron Garage"),
        iron.website_content_path,
    )

    save_website_content(
        WebsiteContent(business_name="Fisio Alameda"),
        fisio.website_content_path,
    )

    assert iron.website_content_path != fisio.website_content_path

    assert (
        load_website_content(
            iron.website_content_path
        ).business_name
        == "Iron Garage"
    )

    assert (
        load_website_content(
            fisio.website_content_path
        ).business_name
        == "Fisio Alameda"
    )


def test_invalid_content_does_not_replace_file(
    tmp_path,
    sample_content,
):
    path = tmp_path / "content.json"

    save_website_content(sample_content, path)

    original = path.read_bytes()

    # Simulamos una modificación inválida
    # posterior a la construcción del modelo.
    sample_content.business_name = ""

    with pytest.raises(ValidationError):
        save_website_content(sample_content, path)

    assert path.read_bytes() == original
