from unittest.mock import Mock

import pytest

from agents.developer_agent import DevelopmentResult
from projects.repair import repair_project
from projects.workspace import build_project_workspace
from specs.storage import save_website_spec
from specs.website_spec import WebsiteSpec


INTERNAL_NOTE = "<p>Información pendiente de completar.</p>"


@pytest.fixture
def project_pair(tmp_path):
    source = build_project_workspace(
        "original",
        projects_directory=tmp_path,
    )

    destination = build_project_workspace(
        "repaired",
        projects_directory=tmp_path,
    )

    source.create_directories()

    specification = WebsiteSpec.model_validate(
        {
            "business": {
                "name": "Taller",
                "business_type": "taller",
                "location": None,
                "services": [],
                "main_goal": None,
                "desired_style": [],
            },
            "navigation": [],
            "primary_cta": None,
            "visual_direction": "Fotografía protagonista.",
            "color_palette": [],
            "typography_direction": "Legible.",
            "sections": [],
            "capabilities": [],
            "missing_content": [],
            "missing_information": [],
            "missing_assets": [],
        }
    )

    save_website_spec(
        specification,
        source.website_spec_path,
    )

    (source.website_directory / "index.html").write_text(
        '<html><head>'
        '<link rel="stylesheet" href="styles.css">'
        '</head><body>'
        f'{INTERNAL_NOTE}'
        '<script src="script.js"></script>'
        '</body></html>',
        encoding="utf-8",
    )

    (source.website_directory / "styles.css").write_text(
        "body { margin: 0; }",
        encoding="utf-8",
    )

    (source.website_directory / "script.js").write_text(
        '"use strict";',
        encoding="utf-8",
    )

    return source, destination


def development_result():
    return DevelopmentResult(
        files_created=[],
        files_modified=["index.html"],
        implementation_notes=["Retirada la nota interna."],
    )


def test_repairs_copy_and_preserves_original(project_pair):
    source, destination = project_pair

    original_html = (
        source.website_directory / "index.html"
    ).read_text(encoding="utf-8")

    def fake_developer(context, workspace):
        assert workspace == destination
        assert "MODE: repair" in context
        assert "public_internal_note" in context

        path = workspace.website_directory / "index.html"

        path.write_text(
            path.read_text(encoding="utf-8").replace(
                INTERNAL_NOTE,
                "",
            ),
            encoding="utf-8",
        )

        return development_result()

    report = repair_project(
        source,
        destination,
        developer_runner=fake_developer,
    )

    assert report.validation.is_valid is True
    assert report.attempts == 1

    assert (
        source.website_directory / "index.html"
    ).read_text(encoding="utf-8") == original_html

    assert (
        destination.root / "config" / "repair_report.json"
    ).is_file()


def test_valid_website_does_not_call_developer(project_pair):
    source, destination = project_pair
    path = source.website_directory / "index.html"

    path.write_text(
        path.read_text(encoding="utf-8").replace(
            INTERNAL_NOTE,
            "",
        ),
        encoding="utf-8",
    )

    runner = Mock()

    report = repair_project(
        source,
        destination,
        developer_runner=runner,
    )

    runner.assert_not_called()
    assert report.attempts == 0
    assert report.validation.is_valid is True


def test_stops_after_attempt_limit(project_pair):
    source, destination = project_pair

    runner = Mock(
        side_effect=lambda context, workspace: development_result()
    )

    report = repair_project(
        source,
        destination,
        max_attempts=2,
        developer_runner=runner,
    )

    assert runner.call_count == 2
    assert report.attempts == 2
    assert report.validation.is_valid is False


def test_requires_saved_contract(project_pair):
    source, destination = project_pair
    source.website_spec_path.unlink()

    runner = Mock()

    with pytest.raises(FileNotFoundError):
        repair_project(
            source,
            destination,
            developer_runner=runner,
        )

    runner.assert_not_called()
    assert not destination.root.exists()


def test_does_not_overwrite_existing_destination(project_pair):
    source, destination = project_pair
    destination.create_directories()

    marker = destination.website_directory / "existing.txt"
    marker.write_text("Conservar", encoding="utf-8")

    runner = Mock()

    with pytest.raises(FileExistsError):
        repair_project(
            source,
            destination,
            developer_runner=runner,
        )

    runner.assert_not_called()
    assert marker.read_text(encoding="utf-8") == "Conservar"


def test_rejects_destination_inside_source(project_pair):
    source, _ = project_pair

    nested = build_project_workspace(
        "nested",
        projects_directory=source.root,
    )

    with pytest.raises(ValueError, match="fuera"):
        repair_project(
            source,
            nested,
            developer_runner=Mock(),
        )

    assert not nested.root.exists()