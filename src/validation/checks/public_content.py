import re
import unicodedata
from html.parser import HTMLParser

from validation.models import ValidationIssue


INTERNAL_NOTE_PATTERNS = [
    r"\binformacion pendiente de completar\b",
    (
        r"\b(?:contexto|contenido) visual pendiente "
        r"de (?:confirmar|validar)\b"
    ),
    (
        r"\bel (?:negocio|cliente) (?:aun )?debe "
        r"(?:confirmar|facilitar|proporcionar)\b"
    ),
    (
        r"\bcuando el (?:negocio|cliente) "
        r"(?:facilite|confirme|proporcione)\b"
    ),
    (
        r"\b(?:horarios?|indicaciones adicionales)\b"
        r"[^.!?]{0,100}\bpendientes? de confirmacion\b"
    ),
    (
        r"\b(?:opiniones|resenas)"
        r"(?: verificadas| de clientes)? "
        r"pendientes? de incorporar\b"
    ),
]


class PublicContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._ignored: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template"}:
            self._ignored.append(tag)
            return

        if self._ignored:
            return

        attributes = dict(attrs)

        for name in ("alt", "title", "placeholder", "aria-label"):
            value = attributes.get(name)

            if value:
                self.parts.append(value)

        if tag == "meta":
            name = (
                attributes.get("name")
                or attributes.get("property")
                or ""
            ).lower()

            if name in {
                "description",
                "og:description",
                "og:title",
            }:
                value = attributes.get("content")

                if value:
                    self.parts.append(value)

    def handle_endtag(self, tag):
        if self._ignored and self._ignored[-1] == tag:
            self._ignored.pop()

    def handle_data(self, data):
        if not self._ignored:
            self.parts.append(data)


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize(
        "NFKD",
        value.casefold(),
    )

    without_accents = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )

    return " ".join(without_accents.split())


def validate_public_content(
    content: str,
) -> list[ValidationIssue]:
    parser = PublicContentParser()
    parser.feed(content)
    parser.close()

    text = normalize_text(" ".join(parser.parts))
    errors: list[ValidationIssue] = []

    for pattern in INTERNAL_NOTE_PATTERNS:
        match = re.search(pattern, text)

        if match is None:
            continue

        errors.append(
            ValidationIssue(
                code="public_internal_note",
                file="index.html",
                message=(
                    "El HTML publica una nota interna: "
                    f"'{match.group(0)}'. "
                    "Retira esa explicación y conserva "
                    "el contenido real disponible. "
                    "Si el bloque solo contiene información "
                    "pendiente, omítelo y ajusta su navegación. "
                    "Registra la carencia en implementation_notes."
                ),
            )
        )

    return errors