from validation.models import ValidationIssue


def validate_javascript(content: str) -> list[ValidationIssue]:

    errors: list[ValidationIssue] = []

    delimiter_stack: list[str] = []

    opening_delimiters = {
        "{": "}",
        "[": "]",
        "(": ")"
    }

    closing_delimiters = {
        "}": "{",
        "]": "[",
        ")": "("
    }

    in_block_comment = False
    in_line_comment = False

    quote: str | None = None
    in_template = False

    escaped = False

    i = 0

    while i < len(content):

        char = content[i]
        next_char = content[i + 1] if i + 1 < len(content) else ""

        if in_block_comment:

            if char == "*" and next_char == "/":
                in_block_comment = False
                i += 2
                continue

            i += 1
            continue


        if in_line_comment:

            if char == "\n":
                in_line_comment = False

            i += 1
            continue


        if quote is not None:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == quote:
                quote = None

            i += 1
            continue


        if in_template:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == "`":
                in_template = False

            i += 1
            continue


        if char == "/" and next_char == "*":
            in_block_comment = True
            i += 2
            continue


        if char == "/" and next_char == "/":
            in_line_comment = True
            i += 2
            continue


        if char in ('"', "'"):
            quote = char
            i += 1
            continue


        if char == "`":
            in_template = True
            i += 1
            continue


        if char in opening_delimiters:

            delimiter_stack.append(char)

            i += 1
            continue


        if char in closing_delimiters:

            expected_opening = closing_delimiters[char]

            if not delimiter_stack or delimiter_stack[-1] != expected_opening:

                errors.append(
                    ValidationIssue(
                        code="unexpected_js_closing_delimiter",
                        file="script.js",
                        message=(
                            f'script.js contiene el delimitador de cierre '
                            f'"{char}" sin una apertura compatible.'
                        )
                    )
                )

                return errors

            delimiter_stack.pop()

        i += 1


    if delimiter_stack:

        errors.append(
            ValidationIssue(
                code="unclosed_js_delimiter",
                file="script.js",
                message=(
                    "script.js contiene uno o más delimitadores "
                    "que no han sido cerrados correctamente."
                )
            )
        )


    if in_block_comment:

        errors.append(
            ValidationIssue(
                code="unclosed_js_block_comment",
                file="script.js",
                message=(
                    "script.js contiene un comentario de bloque "
                    "que no ha sido cerrado correctamente."
                )
            )
        )


    if quote is not None:

        errors.append(
            ValidationIssue(
                code="unclosed_js_string",
                file="script.js",
                message=(
                    "script.js contiene una cadena de texto "
                    "que no ha sido cerrada correctamente."
                )
            )
        )


    if in_template:

        errors.append(
            ValidationIssue(
                code="unclosed_js_template_literal",
                file="script.js",
                message=(
                    "script.js contiene un template literal "
                    "que no ha sido cerrado correctamente."
                )
            )
        )


    return errors