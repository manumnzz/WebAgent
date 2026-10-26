from dataclasses import dataclass
from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectWorkspace:
    project_id: str
    root: Path

    @property
    def website_directory(self) -> Path:
        return self.root /"website"

    @property
    def booking_configuration_path(self) -> Path:
        return self.root / "config" / "booking.json"

    def create_directories(self) -> None:
        self.website_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.booking_configuration_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

def build_project_workspace(
        project_id: str,
        *,
        projects_directory: str | Path | None = None,
) -> ProjectWorkspace:
    if not re.fullmatch(
        r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}",
        project_id,
    ):
        raise ValueError(
            "El identificador debe tener entre 1 y 100 carateres: "
            "letras, números, guiones o guiones bajos. "
            "Debe comenzar por una letra o un número."
        )

    base_directory = (
        Path(projects_directory)
        if projects_directory is not None
        else PROJECT_ROOT / "output" / "projects"
    ).resolve()

    return ProjectWorkspace(
        project_id=project_id,
        root=base_directory / project_id,
    )