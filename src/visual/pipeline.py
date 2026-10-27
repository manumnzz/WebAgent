"""Keep the best technically valid candidate. Every edit happens in a disposable copy."""

from pathlib import Path
from shutil import copytree, rmtree
from tempfile import TemporaryDirectory
from uuid import uuid4

from pydantic import BaseModel, Field

from capabilities.booking.config_loader import load_booking_configuration
from context.context_builders import build_developer_context
from projects.workspace import ProjectWorkspace
from specs.storage import load_website_spec
from state.project_state import ProjectState
from validation.validator import validate_website
from visual.capture import capture_site, review_images
from visual.models import CaptureReport, VisualReview
from visual.reviewer import review_site


class VisualIteration(BaseModel):
    attempt: int
    accepted: bool
    reason: str
    evidence_directory: str
    capture: CaptureReport
    review: VisualReview | None = None


class VisualReport(BaseModel):
    project_id: str
    status: str
    baseline_score: float | None = None
    final_score: float | None = None
    attempts: int = 0
    iterations: list[VisualIteration] = Field(default_factory=list)
    error: str | None = None


def _refine(context, workspace, images):
    from agents.agent_runner import run_agent
    from agents.developer_agent import DEVELOPER_AGENT

    return run_agent(
        agent=DEVELOPER_AGENT,
        user_input=context,
        workspace=workspace,
        image_paths=images,
        max_steps=12,
    )


def _prefer(
    candidate: VisualReview,
    capture: CaptureReport,
    best: VisualReview,
    best_capture: CaptureReport,
) -> bool:
    if capture.blockers > best_capture.blockers:
        return False
    critical = lambda review: sum(i.severity == "high" for i in review.issues)
    if critical(candidate) > critical(best):
        return False
    # A total score must not conceal a newly degraded dimension.
    if any(
        value < best.scores.model_dump()[key] - 1
        for key, value in candidate.scores.model_dump().items()
    ):
        return False
    return (
        (capture.blockers < best_capture.blockers and candidate.score >= best.score)
        or (critical(candidate) < critical(best) and candidate.score >= best.score)
        or candidate.score > best.score
    )


def improve_visual(
    workspace: ProjectWorkspace,
    *,
    max_attempts: int = 2,
    capture_runner=capture_site,
    review_runner=review_site,
    developer_runner=_refine,
) -> VisualReport:
    if not 0 <= max_attempts <= 3:
        raise ValueError("El límite visual debe estar entre 0 y 3.")
    spec = load_website_spec(workspace.website_spec_path)
    booking = (
        load_booking_configuration(workspace.booking_configuration_path)
        if workspace.booking_configuration_path.is_file()
        else None
    )

    def validate(ws):
        return validate_website(
            booking, website_root=ws.website_directory, capabilities=spec.capabilities
        )

    if not validate(workspace).is_valid:
        raise ValueError(
            "Repara primero los errores técnicos antes de pulir el diseño."
        )
    reports = workspace.root / "config" / "visual-review" / uuid4().hex[:12]
    reports.mkdir(parents=True)
    report = VisualReport(project_id=workspace.project_id, status="reviewing")
    try:
        best_directory = reports / "baseline"
        best_capture = capture_runner(workspace.website_directory, best_directory)
        best = review_runner(spec, best_capture, best_directory)
        report.baseline_score = report.final_score = best.score
        report.iterations.append(
            VisualIteration(
                attempt=0,
                accepted=True,
                reason="Referencia inicial.",
                evidence_directory=str(best_directory.relative_to(workspace.root)),
                capture=best_capture,
                review=best,
            )
        )
        for attempt in range(1, max_attempts + 1):
            if best.passed and not best_capture.blockers:
                break
            report.attempts = attempt
            print(
                f"\nRevisión visual {attempt}/{max_attempts}; nota anterior: {best.score}",
                flush=True,
            )
            with TemporaryDirectory(
                prefix="visual-candidate-", dir=workspace.root.parent
            ) as temp:
                candidate = ProjectWorkspace(
                    workspace.project_id, Path(temp) / "project"
                )
                copytree(workspace.website_directory, candidate.website_directory)
                candidate.website_spec_path.parent.mkdir(parents=True)
                candidate.website_spec_path.write_bytes(
                    workspace.website_spec_path.read_bytes()
                )
                context = build_developer_context(
                    ProjectState(website_spec=spec)
                ).replace("MODE: generate", "MODE: visual_refine", 1)
                context += "\nVISUAL_REVIEW:\n" + best.model_dump_json(indent=2)
                context += "\nBROWSER_EVIDENCE:\n" + best_capture.model_dump_json(
                    indent=2
                )
                result = developer_runner(
                    context, candidate, review_images(best_directory)
                )
                if result is None:
                    raise RuntimeError(
                        "DeveloperAgent no devolvió resultado; se conserva la mejor versión."
                    )
                technical = validate(candidate)
                directory = reports / f"attempt-{attempt}"
                if not technical.is_valid:
                    directory.mkdir()
                    (directory / "validation.json").write_text(
                        technical.model_dump_json(indent=2)
                    )
                    report.iterations.append(
                        VisualIteration(
                            attempt=attempt,
                            accepted=False,
                            reason="Regresión técnica. Candidato descartado.",
                            evidence_directory=str(
                                directory.relative_to(workspace.root)
                            ),
                            capture=CaptureReport(),
                        )
                    )
                    break
                capture = capture_runner(candidate.website_directory, directory)
                review = review_runner(spec, capture, directory)
                accepted = _prefer(review, capture, best, best_capture)
                report.iterations.append(
                    VisualIteration(
                        attempt=attempt,
                        accepted=accepted,
                        reason="Mejora aceptada."
                        if accepted
                        else "Sin mejora verificable. Se conserva la versión anterior.",
                        evidence_directory=str(directory.relative_to(workspace.root)),
                        capture=capture,
                        review=review,
                    )
                )
                if not accepted:
                    break
                # Prepare before replacing; restore original if publication fails.
                replacement = workspace.root / f".visual-new-{uuid4().hex}"
                previous = workspace.root / f".visual-old-{uuid4().hex}"
                copytree(candidate.website_directory, replacement)
                workspace.website_directory.rename(previous)
                try:
                    replacement.rename(workspace.website_directory)
                except BaseException:
                    previous.rename(workspace.website_directory)
                    raise
                finally:
                    if replacement.exists():
                        rmtree(replacement)
                rmtree(previous)
                best, best_capture, best_directory = review, capture, directory
                report.final_score = best.score
        report.status = (
            "passed" if best.passed and not best_capture.blockers else "needs_review"
        )
    except Exception as error:
        report.status = "error"
        report.error = f"{type(error).__name__}: {error}"
    finally:
        (reports / "report.json").write_text(
            report.model_dump_json(indent=2), encoding="utf-8"
        )
        (workspace.root / "config" / "visual_report.json").write_text(
            report.model_dump_json(indent=2), encoding="utf-8"
        )
    return report
