from tools.filesystem_tools import WEBSITE_ROOT
from validation.models import ValidationIssue


REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "script.js"
]


def validate_filesystem(website_root=WEBSITE_ROOT) -> list[ValidationIssue]:

    errors: list[ValidationIssue] = []

    for filename in REQUIRED_FILES:

        file_path = website_root / filename

        if not file_path.is_file():

            errors.append(
                ValidationIssue(
                    code="missing_file",
                    file=filename,
                    message=f"El archivo {filename} no existe."
                )
            )

            continue

        content = file_path.read_text(encoding="utf-8")

        if not content.strip():

            errors.append(
                ValidationIssue(
                    code="empty_file",
                    file=filename,
                    message=f"El archivo {filename} está vacío."
                )
            )

    return errors