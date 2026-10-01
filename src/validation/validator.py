from pydantic import BaseModel

from tools.filesystem_tools import WEBSITE_ROOT


class ValidationIssue(BaseModel):
    code: str
    file: str | None = None
    message: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationIssue]


REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "script.js"
]


def validate_html(content: str) -> list[ValidationIssue]:

    errors: list[ValidationIssue] = []

    lower_content = content.lower()

    if "<html" not in lower_content:
        errors.append(
            ValidationIssue(
                code="missing_html_tag",
                file="index.html",
                message="index.html no contiene la etiqueta <html>."
            )
        )

    if "</html>" not in lower_content:
        errors.append(
            ValidationIssue(
                code="missing_html_closing_tag",
                file="index.html",
                message="index.html no contiene la etiqueta de cierre </html>."
            )
        )

    if "styles.css" not in content:
        errors.append(
            ValidationIssue(
                code="missing_stylesheet_reference",
                file="index.html",
                message="index.html no referencia styles.css."
            )
        )

    if "script.js" not in content:
        errors.append(
            ValidationIssue(
                code="missing_script_reference",
                file="index.html",
                message="index.html no referencia script.js."
            )
        )

    return errors


def validate_website() -> ValidationResult:

    errors: list[ValidationIssue] = []

    for filename in REQUIRED_FILES:

        file_path = WEBSITE_ROOT / filename

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

            continue

        if filename == "index.html":
            errors.extend(validate_html(content))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )