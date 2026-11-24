from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

import pytest

from capabilities.implementations.maps import build_maps_implementation
from validation.checks.capability_placement import CapabilityInstanceParser


class MapMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.elements = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.elements[tag] = dict(attrs)


def test_maps_embeds_a_square_and_keeps_the_google_maps_link():
    address = 'Calle Sierpes 15, Sevilla & "Centro"'
    implementation = build_maps_implementation(f"  {address}  ")
    markup = MapMarkup(implementation.html)
    frame = markup.elements["iframe"]
    link = markup.elements["a"]

    assert implementation.type == "maps"
    assert frame["width"] == frame["height"]
    assert frame["title"]
    assert frame["loading"] == "lazy"
    assert parse_qs(urlsplit(frame["src"]).query) == {"q": [address], "output": ["embed"]}
    assert parse_qs(urlsplit(link["href"]).query) == {"api": ["1"], "query": [address]}
    assert link["class"] == "capability-maps"
    assert "aspect-ratio: 1" in implementation.css
    assert "width: 100%" in implementation.css

    placement = CapabilityInstanceParser()
    placement.feed(f'<section data-capability-zone="contact">{implementation.html}</section>')
    assert placement.zones["maps"] == ["contact"]


def test_maps_requires_a_business_address():
    with pytest.raises(ValueError, match="dirección"):
        build_maps_implementation(" ")
