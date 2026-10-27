from html.parser import HTMLParser
from urllib.parse import parse_qs, unquote, urlsplit

from capabilities.models.booking import BookingConfiguration
from validation.models import ValidationIssue


class _ActionLinks(HTMLParser):
    """Collect link labels and the links reachable inside each fragment target."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.targets: dict[str, list[str]] = {}
        self._active: list[dict[str, str]] = []
        self._elements: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        target = attributes.get("id")
        if target:
            self.targets.setdefault(target, [])
        if tag not in self.VOID_TAGS:
            self._elements.append((tag, target))
        if tag == "a":
            href = attributes.get("href") or ""
            self._active.append({"href": href, "text": ""})
            for _, target_id in self._elements:
                if target_id:
                    self.targets[target_id].append(href)

    def handle_data(self, data):
        for anchor in self._active:
            anchor["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._active:
            anchor = self._active.pop()
            self.links.append((anchor["text"], anchor["href"]))
        for index in range(len(self._elements) - 1, -1, -1):
            if self._elements[index][0] == tag:
                del self._elements[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID_TAGS:
            self.handle_endtag(tag)


def validate_booking_inquiry_links(
    html: str, configuration: BookingConfiguration
) -> list[ValidationIssue]:
    """Budget actions must reach a real inquiry, directly or through in-page navigation."""
    quote_ids = {
        option.id
        for option in configuration.inquiry_types
        if "presupuest" in option.name.casefold()
    }
    if not quote_ids:
        return []
    parser = _ActionLinks()
    parser.feed(html)
    budget_links = [
        href for label, href in parser.links if "presupuest" in label.casefold()
    ]

    def reaches_inquiry(href: str) -> bool:
        pending = [href]
        visited = set()
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            try:
                url = urlsplit(current)
            except ValueError:
                continue
            if url.scheme or url.netloc:
                continue
            if url.path == "/reservar" and not url.fragment:
                ids = parse_qs(url.query, keep_blank_values=True).get("service_id", [])
                if len(ids) == 1 and ids[0] in quote_ids:
                    return True
            if current.startswith("#") and not url.path and not url.query:
                pending.extend(parser.targets.get(unquote(url.fragment), []))
        return False

    if budget_links and all(reaches_inquiry(href) for href in budget_links):
        return []
    return [
        ValidationIssue(
            code="invalid_budget_link",
            file="index.html",
            message=(
                "Los botones de presupuesto deben enlazar a /reservar?service_id=<id de consulta> "
                "o a un ancla que conduzca a esa acción real. No uses mailto:, destinos externos, "
                "anclas vacías ni un formulario alternativo para presupuestos."
            ),
        )
    ]
