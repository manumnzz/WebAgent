from collections.abc import Callable
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory

from pydantic import BaseModel, Field

from agents.developer_agent import DevelopmentResult
from capabilities.booking.config_loader import (
    load_booking_configuration,
)
from context.context_builders import (
    build_developer_repair_context,
)
from projects.workspace import ProjectWorkspace
from specs.storage import load_website_spec
from state.project_state import ProjectState
from validation.models import ValidationResult
from validation.validator import validate_website


DeveloperRunner = Callable[
    [str, ProjectWorkspace],
    DevelopmentResult | None,
]


class RepairReport(BaseModel):
    source_project_id: str
    project_id: str
    attempts: int
    validation: ValidationResult
    implementation_notes: list[str] = Field(
        default_factory=list,
    )


def _run_developer(
    context: str,
    workspace: ProjectWorkspace,
) -> DevelopmentResult | None:
    from agents.agent_runner import run_agent
    from agents.developer_agent import DEVELOPER_AGENT

    return run_agent(
        agent=DEVELOPER_AGENT,
        user_input=context,
        workspace=workspace,
    )


def repair_project(
    source: ProjectWorkspace,
    destination: ProjectWorkspace,
    *,
    max_attempts: int = 2,
    developer_runner: DeveloperRunner | None = None,
) -> RepairReport:
    if max_attempts < 1:
        raise ValueError(
            "Debe permitirse al menos un intento de reparación."
        )

    specification = load_website_spec(
        source.website_spec_path,
    )

    if not (source.website_directory / "index.html").is_file():
        raise FileNotFoundError(
            "El proyecto original no contiene website/index.html."
        )

    source_root = source.root.resolve()
    destination_root = destination.root.resolve()

    if destination_root.is_relative_to(source_root):
        raise ValueError(
            "La copia debe estar fuera del proyecto original."
        )

    if destination_root.exists():
        raise FileExistsError(
            f"El destino ya existe: {destination.project_id}"
        )

    booking_required = any(
        capability.type == "booking" and capability.ready
        for capability in specification.capabilities
    )

    if (
        booking_required
        and not source.booking_configuration_path.is_file()
    ):
        raise FileNotFoundError(
            "El contrato requiere Booking, pero falta booking.json."
        )

    booking_configuration = (
        load_booking_configuration(
            source.booking_configuration_path,
        )
        if source.booking_configuration_path.is_file()
        else None
    )

    destination_root.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with TemporaryDirectory(
        dir=destination_root.parent,
        prefix="project-repair-",
    ) as temporary_directory:
        prepared = Path(temporary_directory) / "project"

        copytree(source_root, prepared)
        prepared.rename(destination_root)

    state = ProjectState(
        website_spec=specification,
    )

    attempts = 0
    notes: list[str] = []

    while True:
        state.validation = validate_website(
            booking_configuration,
            website_root=destination.website_directory,
            capabilities=specification.capabilities,
        )

        if (
            state.validation.is_valid
            or attempts >= max_attempts
        ):
            break

        attempts += 1

        print(
            f"\nReparación {attempts}/{max_attempts}",
            flush=True,
        )

        context = build_developer_repair_context(state)
        runner = developer_runner or _run_developer

        result = runner(context, destination)

        if result is None:
            raise RuntimeError(
                "DeveloperAgent no devolvió un resultado. "
                "La copia queda disponible para inspección."
            )

        state.development = result
        notes.extend(result.implementation_notes)

    report = RepairReport(
        source_project_id=source.project_id,
        project_id=destination.project_id,
        attempts=attempts,
        validation=state.validation,
        implementation_notes=notes,
    )

    report_path = (
        destination.root / "config" / "repair_report.json"
    )

    report_path.write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return report