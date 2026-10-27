from unittest.mock import Mock
import pytest
from agents.developer_agent import DevelopmentResult
from projects.workspace import build_project_workspace
from specs.storage import save_website_spec
from specs.website_spec import WebsiteSpec
from visual.models import CaptureReport, BrowserFinding, VisualReview, VisualScores
from visual.pipeline import improve_visual


@pytest.fixture
def workspace(tmp_path):
    ws = build_project_workspace("visual-test", projects_directory=tmp_path)
    ws.create_directories()
    save_website_spec(
        WebsiteSpec.model_validate(
            {
                "business": {
                    "name": "Negocio",
                    "business_type": "taller",
                    "location": "Sevilla",
                    "services": ["Revisiones"],
                    "main_goal": "Consultas",
                    "desired_style": [],
                },
                "navigation": [],
                "primary_cta": None,
                "visual_direction": "Clara",
                "color_palette": ["#FFFFFF"],
                "typography_direction": "Sans",
                "sections": [],
                "capabilities": [],
                "missing_content": [],
                "missing_information": [],
                "missing_assets": [],
            }
        ),
        ws.website_spec_path,
    )
    (ws.website_directory / "index.html").write_text(
        '<html><head><link rel="stylesheet" href="styles.css"></head><body><h1>Negocio</h1><script src="script.js"></script></body></html>'
    )
    (ws.website_directory / "styles.css").write_text("body { margin: 0; }")
    (ws.website_directory / "script.js").write_text('"use strict";')
    return ws


def review(score):
    return VisualReview(
        scores=VisualScores(**{n: score for n in VisualScores.model_fields}),
        strengths=["Legible"],
        issues=[],
        summary="Simulada",
    )


def capture(website, directory):
    directory.mkdir(parents=True)
    return CaptureReport()


def refine(context, workspace, images):
    assert "MODE: visual_refine" in context and "VISUAL_REVIEW:" in context
    (workspace.website_directory / "styles.css").write_text(
        "body { margin: 0; color: #111; }"
    )
    return DevelopmentResult(
        files_created=[], files_modified=["styles.css"], implementation_notes=[]
    )


def test_accepts_improvement_and_stops(workspace):
    developer = Mock(side_effect=refine)
    report = improve_visual(
        workspace,
        capture_runner=capture,
        review_runner=Mock(side_effect=[review(6), review(8)]),
        developer_runner=developer,
    )
    assert (
        report.status == "passed"
        and report.baseline_score == 60
        and report.final_score == 80
    )
    assert developer.call_count == 1
    assert "color: #111" in (workspace.website_directory / "styles.css").read_text()
    assert (workspace.root / "config/visual_report.json").is_file()


def test_discards_worse_candidate(workspace):
    before = (workspace.website_directory / "styles.css").read_bytes()
    report = improve_visual(
        workspace,
        capture_runner=capture,
        review_runner=Mock(side_effect=[review(7), review(6)]),
        developer_runner=refine,
    )
    assert report.status == "needs_review" and report.final_score == 70
    assert not report.iterations[-1].accepted
    assert (workspace.website_directory / "styles.css").read_bytes() == before


def test_technical_regression_preserves_original(workspace):
    before = (workspace.website_directory / "index.html").read_bytes()

    def bad(context, candidate, images):
        (candidate.website_directory / "index.html").unlink()
        return DevelopmentResult(
            files_created=[], files_modified=[], implementation_notes=[]
        )

    reviewer = Mock(return_value=review(6))
    report = improve_visual(
        workspace, capture_runner=capture, review_runner=reviewer, developer_runner=bad
    )
    assert reviewer.call_count == 1 and not report.iterations[-1].accepted
    assert (workspace.website_directory / "index.html").read_bytes() == before


def test_capture_failure_reports_error_without_modification(workspace):
    before = (workspace.website_directory / "styles.css").read_bytes()
    report = improve_visual(
        workspace, capture_runner=Mock(side_effect=RuntimeError("browser unavailable"))
    )
    assert report.status == "error" and report.final_score is None
    assert "browser unavailable" in report.error
    assert (workspace.website_directory / "styles.css").read_bytes() == before


def test_model_failure_keeps_best(workspace):
    before = (workspace.website_directory / "styles.css").read_bytes()
    report = improve_visual(
        workspace,
        capture_runner=capture,
        review_runner=Mock(return_value=review(6)),
        developer_runner=Mock(side_effect=RuntimeError("model unavailable")),
    )
    assert report.status == "error"
    assert (workspace.website_directory / "styles.css").read_bytes() == before


def test_good_baseline_needs_no_developer(workspace):
    developer = Mock()
    report = improve_visual(
        workspace,
        capture_runner=capture,
        review_runner=Mock(return_value=review(8)),
        developer_runner=developer,
    )
    assert report.status == "passed" and report.attempts == 0
    developer.assert_not_called()


def test_zero_attempts_reviews_only(workspace):
    developer = Mock()
    report = improve_visual(
        workspace,
        max_attempts=0,
        capture_runner=capture,
        review_runner=Mock(return_value=review(5)),
        developer_runner=developer,
    )
    assert report.status == "needs_review" and report.attempts == 0
    developer.assert_not_called()


def test_new_browser_blocker_rejects_higher_score(workspace):
    before = (workspace.website_directory / "styles.css").read_bytes()
    reports = iter(
        [
            CaptureReport(),
            CaptureReport(
                findings=[
                    BrowserFinding(
                        code="overflow",
                        viewport="mobile",
                        detail="overflow",
                        blocking=True,
                    )
                ]
            ),
        ]
    )

    def bad_capture(website, directory):
        directory.mkdir(parents=True)
        return next(reports)

    report = improve_visual(
        workspace,
        capture_runner=bad_capture,
        review_runner=Mock(side_effect=[review(6), review(9)]),
        developer_runner=refine,
    )
    assert not report.iterations[-1].accepted and report.final_score == 60
    assert (workspace.website_directory / "styles.css").read_bytes() == before


@pytest.mark.parametrize("limit", [-1, 4])
def test_rejects_unbounded_iterations(workspace, limit):
    with pytest.raises(ValueError):
        improve_visual(workspace, max_attempts=limit)
