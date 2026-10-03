from tools.filesystem_tools import WEBSITE_ROOT
from validation.models import ValidationIssue, ValidationResult
from validation.html_parser import WebsiteHTMLParser
from validation.checks.filesystem_checks import validate_filesystem
from validation.checks.html_checks import validate_html
from validation.checks.css_checks import validate_css
from validation.checks.javascript_checks import validate_javascript

def validate_website() -> ValidationResult:

    errors: list[ValidationIssue] = []

    errors.extend(validate_filesystem())

    #index.html
    index_path = WEBSITE_ROOT / "index.html"

    if index_path.is_file():

        content = index_path.read_text(encoding="utf-8")

        if content.strip():
            errors.extend(validate_html(content))

    #styles.css
    styles_path = WEBSITE_ROOT / "styles.css"

    if styles_path.is_file():

        content = styles_path.read_text(encoding="utf-8")

        if content.strip():
            errors.extend(validate_css(content))

    #script.js
    script_path = WEBSITE_ROOT / "script.js"

    if script_path.is_file():

        content = script_path.read_text(encoding="utf-8")

        if content.strip():
            errors.extend(validate_javascript(content))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )