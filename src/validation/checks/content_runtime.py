from collections.abc import Sequence
from html.parser import HTMLParser
from pathlib import Path

from content.presentation import RUNTIME_NAME, RUNTIME_PATH
from specs.website_spec import WebsiteCapabilitySpec
from validation.models import ValidationIssue

LIST_FIELDS = {
    "services": {"name", "description", "price"},
    "opening_hours": {"day", "hours"},
    "gallery": {"image"},
}
CONTACT_BINDINGS = {
    "phone": {"text:phone", "link:tel"},
    "whatsapp": {"text:whatsapp", "link:whatsapp"},
    "email": {"text:email", "link:email"},
    "address": {"text:address", "link:maps"},
}
CAPABILITY_BINDINGS = {
    "whatsapp": ("a", "capability-whatsapp", "whatsapp"),
    "maps": ("a", "capability-maps", "maps"),
    "contact_form": ("form", "capability-contact-form", "email"),
}
_TEMPLATE_FIELDS = object()
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class ContentMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.scripts = 0
        self.lists: dict[str, list[set[str]]] = {}
        self.bindings: set[str] = set()
        self.capabilities: set[str] = set()
        self.unbound_capabilities: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        direct_parent = self.stack[-1][1] if self.stack else {}
        if tag not in VOID_TAGS:
            self.stack.append((tag, attrs))

        if tag == "script" and attrs.get("src") in {RUNTIME_NAME, f"./{RUNTIME_NAME}"}:
            if "defer" in attrs and "async" not in attrs and not attrs.get("type"):
                self.scripts += 1

        if tag == "template" and "data-content-item" in attrs:
            name = direct_parent.get("data-content-list")
            if name in LIST_FIELDS and "hidden" in direct_parent:
                classes = (direct_parent.get("class") or "").split()
                if name != "gallery" or "capability-gallery" in classes:
                    fields = set()
                    self.lists.setdefault(name, []).append(fields)
                    attrs[_TEMPLATE_FIELDS] = fields

        template = next(
            (parent for parent_tag, parent in reversed(self.stack) if parent_tag == "template"),
            None,
        )
        if template is not None:
            fields = template.get(_TEMPLATE_FIELDS)
            if fields is not None:
                if "data-content-field" in attrs and tag not in VOID_TAGS:
                    fields.add(attrs["data-content-field"])
                if tag == "img" and "data-content-image" in attrs and "src" not in attrs:
                    fields.add("image")
            return

        if "data-content-text" in attrs and tag not in VOID_TAGS:
            self.bindings.add(f'text:{attrs["data-content-text"]}')

        link = attrs.get("data-content-link")
        bound_link = (
            link and "hidden" in attrs
            and (
                (tag == "a" and "href" not in attrs)
                or (tag == "form" and link == "email" and "action" not in attrs)
            )
        )
        if bound_link:
            self.bindings.add(f"link:{link}")

        classes = (attrs.get("class") or "").split()
        for capability, (expected_tag, expected_class, expected_link) in CAPABILITY_BINDINGS.items():
            if tag == expected_tag and expected_class in classes:
                if bound_link and link == expected_link:
                    self.capabilities.add(capability)
                else:
                    self.unbound_capabilities.add(capability)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def validate_content_runtime(
    markup: str,
    website_root: Path,
    capabilities: Sequence[WebsiteCapabilitySpec],
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []

    def report(message: str, file: str = "index.html") -> None:
        errors.append(ValidationIssue(code="invalid_content_binding", file=file, message=message))

    runtime = website_root / RUNTIME_NAME
    if not runtime.is_file() or runtime.read_bytes() != RUNTIME_PATH.read_bytes():
        report("Falta el script de contenido instalado por WebAgent o ha sido modificado.", RUNTIME_NAME)

    parser = ContentMarkup()
    parser.feed(markup)
    parser.close()

    if parser.scripts != 1:
        report(f'Carga una sola vez <script src="{RUNTIME_NAME}" defer></script>.')

    expected_lists = ["services", "opening_hours"]
    if any(capability.type == "gallery" for capability in capabilities):
        expected_lists.append("gallery")
    for name in expected_lists:
        templates = parser.lists.get(name, [])
        expected = LIST_FIELDS[name]
        if not templates or any(not expected.issubset(fields) for fields in templates):
            report(
                f'Completa data-content-list="{name}" con hidden y un template hijo '
                f'que contenga los campos: {", ".join(sorted(expected))}.'
            )

    for field, bindings in CONTACT_BINDINGS.items():
        if not bindings.intersection(parser.bindings):
            report(f"Vincula el contacto '{field}' a content.json mediante los marcadores del contrato.")

    for capability in capabilities:
        name = capability.type
        if capability.ready and name in CAPABILITY_BINDINGS and (
            name not in parser.capabilities or name in parser.unbound_capabilities
        ):
            report(f"Usa el fragmento editable para cada instancia de la capability '{name}'.")

    return errors
