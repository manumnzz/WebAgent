from pathlib import Path
from uuid import uuid4

from intake.models import ProjectInput


def save_project_input(
        project_input: ProjectInput,
        storage_directory: str | Path,
) -> str:
    submission_id = uuid4().hex

    submission_directory = (
        Path(storage_directory) / submission_id
    )

    submission_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    input_file = (
        submission_directory / "project_input.json"
    )

    input_file.write_text(
        project_input.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return submission_id