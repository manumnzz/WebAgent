from validation.models import ValidationIssue


def validate_css(content: str) -> list[ValidationIssue]:

    errors: list[ValidationIssue] = []

    brace_depth = 0

    in_comment = False
    quote: str | None = None
    escaped = False

    i = 0

    while i < len(content):

        char = content[i]
        next_char = content[i + 1] if i + 1 < len(content) else ""

        # Estamos dentro de un comentario /* ... */
        if in_comment:

            if char == "*" and next_char == "/":
                in_comment = False
                i += 2
                continue

            i += 1
            continue

        # Estamos dentro de una cadena "..." o '...'
        if quote is not None:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == quote:
                quote = None

            i += 1
            continue

        # Inicio de comentario
        if char == "/" and next_char == "*":
            in_comment = True
            i += 2
            continue

        # Inicio de string
        if char in ('"', "'"):
            quote = char
            i += 1
            continue

        # Apertura de bloque CSS
        if char == "{":
            brace_depth += 1

        # Cierre de bloque CSS
        elif char == "}":

            brace_depth -= 1

            if brace_depth < 0:

                errors.append(
                    ValidationIssue(
                        code="unexpected_css_closing_brace",
                        file="styles.css",
                        message=(
                            "styles.css contiene una llave de cierre "
                            "sin una apertura correspondiente."
                        )
                    )
                )

                return errors

        i += 1

    if brace_depth > 0:

        errors.append(
            ValidationIssue(
                code="unclosed_css_block",
                file="styles.css",
                message=(
                    "styles.css contiene uno o más bloques "
                    "que no han sido cerrados correctamente."
                )
            )
        )

    if in_comment:

        errors.append(
            ValidationIssue(
                code="unclosed_css_comment",
                file="styles.css",
                message=(
                    "styles.css contiene un comentario CSS "
                    "que no ha sido cerrado correctamente."
                )
            )
        )

    if quote is not None:

        errors.append(
            ValidationIssue(
                code="unclosed_css_string",
                file="styles.css",
                message=(
                    "styles.css contiene una cadena de texto "
                    "que no ha sido cerrada correctamente."
                )
            )
        )

    return errors