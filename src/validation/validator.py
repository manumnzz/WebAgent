from tools.filesystem_tools import WEBSITE_ROOT
from validation.models import ValidationIssue, ValidationResult
from validation.html_parser import WebsiteHTMLParser
from validation.checks.filesystem_checks import validate_filesystem
from validation.checks.html_checks import validate_html
from validation.checks.css_checks import validate_css
from validation.checks.javascript_checks import validate_javascript
from validation.checks.booking_links import validate_booking_inquiry_links
from capabilities.models.booking import BookingConfiguration
from pathlib import Path



def validate_website(
    booking_configuration: BookingConfiguration | None = None,
    *,
    website_root: Path = WEBSITE_ROOT,
) -> ValidationResult:

    errors: list[ValidationIssue] = []

    errors.extend(
        validate_filesystem(
            website_root=website_root,
        )
    )

    #index.html
    index_path = website_root / "index.html"

    if index_path.is_file():

        content = index_path.read_text(encoding="utf-8")

        if content.strip():
            errors.extend(validate_html(content))
            if booking_configuration is not None:
                errors.extend(validate_booking_inquiry_links(
                    content, booking_configuration,
                ))

    #styles.css
    styles_path = website_root / "styles.css"

    if styles_path.is_file():

        content = styles_path.read_text(encoding="utf-8")

        if content.strip():
            errors.extend(validate_css(content))

    #script.js
    script_path = website_root / "script.js"

    if script_path.is_file():

        content = script_path.read_text(encoding="utf-8")

        if content.strip():
            errors.extend(validate_javascript(content))

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
