from collections import Counter, defaultdict
from collections.abc import Sequence
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from specs.website_spec import WebsiteCapabilitySpec
from validation.models import ValidationIssue

from capabilities.placement_policy import (
    CapabilityPlacementPolicy,
)


VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr",
    "img", "input", "link", "meta", "param",
    "source", "track", "wbr",
}


class CapabilityInstanceParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.counts: Counter[str] = Counter()

        self.zones: dict[str, list[str | None]] = defaultdict(
            list,
        )

        self._open_elements: list[
            tuple[str, str | None]
        ] = []

        self.booking_option_ids: set[str] = set()
        self.invalid_booking_targets = 0

    def _record(
        self,
        capability_type: str,
        zone: str | None,
    ):
        self.counts[capability_type] += 1
        self.zones[capability_type].append(zone)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        inherited_zone = (
            self._open_elements[-1][1]
            if self._open_elements
            else None
        )

        if "data-capability-zone" in attributes:
            zone = attributes["data-capability-zone"] or ""
        else:
            zone = inherited_zone

        if tag not in VOID_TAGS:
            self._open_elements.append((tag, zone))

        classes = set(
            (attributes.get("class") or "").split()
        )

        if "capability-gallery" in classes:
            self._record("gallery", zone)

        if "capability-reviews" in classes:
            self._record("reviews", zone)

        if (
            tag == "form"
            and "capability-contact-form" in classes
        ):
            self._record("contact_form", zone)

        if tag != "a":
            return

        href = (attributes.get("href") or "").strip()

        if href.startswith("#"):
            return

        try:
            url = urlsplit(href)
            host = (url.hostname or "").lower()
        except ValueError:
            return

        if (
            "capability-whatsapp" in classes
            or host in {
                "wa.me",
                "api.whatsapp.com",
                "web.whatsapp.com",
            }
        ):
            self._record("whatsapp", zone)

        if (
            "capability-maps" in classes
            or (
                host in {"google.com", "www.google.com"}
                and (
                    url.path == "/maps"
                    or url.path.startswith("/maps/")
                )
            )
        ):
            self._record("maps", zone)

        is_local_booking = (
            not url.scheme
            and not url.netloc
            and url.path == "/reservar"
        )

        if is_local_booking:
            query = parse_qs(
                url.query,
                keep_blank_values=True,
            )

            if "service_id" not in query:
                self._record("booking", zone)
            else:
                option_ids = query["service_id"]

                if (
                    len(option_ids) != 1
                    or not option_ids[0].strip()
                ):
                    self.invalid_booking_targets += 1
                    return

                option_id = option_ids[0]
                self.booking_option_ids.add(option_id)

                self._record(
                    f"booking_option:{option_id}",
                    zone,
                )

    def handle_endtag(self, tag):
        for index in range(
            len(self._open_elements) - 1,
            -1,
            -1,
        ):
            if self._open_elements[index][0] == tag:
                del self._open_elements[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

        if tag not in VOID_TAGS:
            self.handle_endtag(tag)


def _validate_instance_group(
    label: str,
    zones: Sequence[str | None],
    policy: CapabilityPlacementPolicy,
) -> list[ValidationIssue]:
    errors: list[ValidationIssue] = []
    count = len(zones)

    if count > policy.max_instances:
        errors.append(
            ValidationIssue(
                code="capability_instance_limit_exceeded",
                file="index.html",
                message=(
                    f"'{label}' aparece {count} veces. "
                    "El máximo permitido es "
                    f"{policy.max_instances}. "
                    "Elimina las instancias sobrantes "
                    "conservando su funcionamiento."
                ),
            )
        )

    if policy.allowed_zones is None:
        return errors

    for instance_number, zone in enumerate(zones, start=1):
        if zone in policy.allowed_zones:
            continue

        code = (
            "missing_capability_zone"
            if zone is None
            else "invalid_capability_zone"
        )

        description = (
            "no tiene una zona declarada"
            if zone is None
            else f"está en la zona '{zone}'"
        )

        errors.append(
            ValidationIssue(
                code=code,
                file="index.html",
                message=(
                    f"La instancia {instance_number} "
                    f"de '{label}' {description}. "
                    "Debe estar en una de estas zonas: "
                    f"{', '.join(policy.allowed_zones)}. "
                    "Utiliza data-capability-zone "
                    "en el elemento o en su contenedor."
                ),
            )
        )

    return errors


def validate_capability_placement(
    content: str,
    capabilities: Sequence[WebsiteCapabilitySpec],
) -> list[ValidationIssue]:
    parser = CapabilityInstanceParser()
    parser.feed(content)
    parser.close()

    errors: list[ValidationIssue] = []

    for capability in capabilities:
        if not capability.ready:
            continue

        policy = capability.placement_policy

        errors.extend(
            _validate_instance_group(
                capability.type,
                parser.zones[capability.type],
                policy,
            )
        )

        if capability.type != "booking":
            continue

        for option_id in sorted(parser.booking_option_ids):
            errors.extend(
                _validate_instance_group(
                    f"booking, opción '{option_id}'",
                    parser.zones[
                        f"booking_option:{option_id}"
                    ],
                    policy,
                )
            )

        if parser.invalid_booking_targets:
            errors.append(
                ValidationIssue(
                    code="invalid_booking_target",
                    file="index.html",
                    message=(
                        "Hay enlaces de Booking con service_id "
                        "vacío o repetido en la misma URL. "
                        "Cada enlace específico debe contener "
                        "un único service_id no vacío."
                    ),
                )
            )

    return errors