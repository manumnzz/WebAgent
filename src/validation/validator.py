from pydantic import BaseModel
from html.parser import HTMLParser
from collections import Counter

from tools.filesystem_tools import WEBSITE_ROOT


class ValidationIssue(BaseModel):
    code: str
    file: str | None = None
    message: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationIssue]

class WebsiteHTMLParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.start_tags: set[str] = set()
        self.end_tags: set[str] = set()

        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.ids: list[str] = []
        self.internal_links: list[str] = []

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()

        self.start_tags.add(tag)

        attrs_dict = dict(attrs)

        if tag == "a":

            href = attrs_dict.get("href")

            if href and href.startswith("#") and len(href) > 1:
                self.internal_links.append(href[1:])

        if tag == "link":

            rel = attrs_dict.get("rel", "")
            href = attrs_dict.get("href")

            if "stylesheet" in rel.lower().split() and href:
                self.stylesheets.append(href)

        if tag == "script":

            src = attrs_dict.get("src")

            if src:
                self.scripts.append(src)

        element_id = attrs_dict.get("id")

        if element_id:
            self.ids.append(element_id)

    def handle_endtag(self, tag):

        self.end_tags.add(tag.lower())
    


REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "script.js"
]


def validate_html(content: str) -> list[ValidationIssue]:

    errors: list[ValidationIssue] = []

    parser = WebsiteHTMLParser()

    parser.feed(content)

    id_counts = Counter(parser.ids)

    for element_id, count in id_counts.items():

        if count > 1:

            errors.append(
                ValidationIssue(
                    code="duplicate_html_id",
                    file="index.html",
                    message=(
                        f'El id "{element_id}" aparece'
                        f' {count} veces en index.html.'
                    )
                )
            )
            
    existing_ids = set(parser.ids)

    for target_id in parser.internal_links:

        if target_id not in existing_ids:

            errors.append(
                ValidationIssue(
                    code="broken_internal_link",
                    file="index.html",
                    message=(
                        f'El enlace interno "#{target_id}" '
                        f"no apunta a ningún id existente."
                    )
                )
            )

    if "html" not in parser.start_tags:

        errors.append(
            ValidationIssue(
                code="missing_html_tag",
                file="index.html",
                message="index.html no contiene la etiqueta <html>."
            )
        )


    if "html" not in parser.end_tags:

        errors.append(
            ValidationIssue(
                code="missing_html_closing_tag",
                file="index.html",
                message="index.html no contiene la etiqueta de cierre </html>."
            )
        )


    if "head" not in parser.start_tags:

        errors.append(
            ValidationIssue(
                code="missing_head_tag",
                file="index.html",
                message="index.html no contiene la etiqueta <head>."
            )
        )


    if "body" not in parser.start_tags:

        errors.append(
            ValidationIssue(
                code="missing_body_tag",
                file="index.html",
                message="index.html no contiene la etiqueta <body>."
            )
        )


    if "styles.css" not in parser.stylesheets:

        errors.append(
            ValidationIssue(
                code="missing_stylesheet_reference",
                file="index.html",
                message="index.html no enlaza styles.css como hoja de estilos."
            )
        )


    if "script.js" not in parser.scripts:

        errors.append(
            ValidationIssue(
                code="missing_script_reference",
                file="index.html",
                message="index.html no carga script.js mediante una etiqueta <script>."
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