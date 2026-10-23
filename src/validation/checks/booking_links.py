from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from capabilities.models.booking import BookingConfiguration
from validation.models import ValidationIssue


class _ActionLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._active: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._active.append({"href": dict(attrs).get("href", ""), "text": ""})

    def handle_data(self, data):
        for anchor in self._active:
            anchor["text"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._active:
            anchor = self._active.pop()
            self.links.append((anchor["text"], anchor["href"]))


def validate_booking_inquiry_links(
    html: str, configuration: BookingConfiguration
) -> list[ValidationIssue]:
    """Keep generated budget actions connected to their configured inquiry."""
    quote_ids = {
        option.id for option in configuration.inquiry_types
        if "presupuest" in option.name.casefold()
    }
    if not quote_ids:
        return []

    parser = _ActionLinks()
    parser.feed(html)
    budget_links = [
        href for label, href in parser.links
        if "presupuest" in label.casefold()
    ]
    if budget_links and all(
        urlsplit(href).path == "/reservar"
        and any(option_id in parse_qs(urlsplit(href).query).get("service_id", [])
                for option_id in quote_ids)
        for href in budget_links
    ):
        return []

    return [ValidationIssue(
        code="invalid_budget_link",
        file="index.html",
        message=(
            "Los botones de presupuesto deben enlazar a "
            "/reservar?service_id=<id de consulta> para registrar la "
            "solicitud en Calendar; no uses mailto: ni un formulario "
            "alternativo para presupuestos."
        ),
    )]
