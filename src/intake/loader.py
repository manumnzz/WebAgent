from pathlib import Path
from intake.models import ProjectInput

def load_project_input(
        path: str | Path,
) -> ProjectInput:
    content = Path(path).read_text(
        encoding="utf-8"
    )

    return ProjectInput.model_validate_json(
        content
    )

