from collections import Counter

from validation.models import ValidationIssue
from validation.html_parser import WebsiteHTMLParser


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
                        f'El id "{element_id}" aparece '
                        f'{count} veces en index.html.'
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