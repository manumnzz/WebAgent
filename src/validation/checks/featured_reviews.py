from collections.abc import Sequence
from html.parser import HTMLParser

from capabilities.models.review import ReviewData
from specs.website_spec import WebsiteCapabilitySpec
from validation.models import ValidationIssue


class ReviewMarkup(HTMLParser):
    fields = {
        "capability-review-text": "texts",
        "capability-review-author": "authors",
        "capability-reviews-label": "labels",
    }

    def __init__(self):
        super().__init__()
        self.texts = []
        self.authors = []
        self.labels = []
        self.ratings = []
        self.links = []
        self.capture = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        for css_class in classes:
            if css_class in self.fields:
                self.capture = (tag, getattr(self, self.fields[css_class]), [])
        if "capability-review-rating" in classes:
            self.ratings.append(attrs.get("aria-label"))
        if tag == "a" and "capability-reviews-source" in classes:
            self.links.append(attrs.get("href"))

    def handle_data(self, data):
        if self.capture:
            self.capture[2].append(data)

    def handle_endtag(self, tag):
        if self.capture and self.capture[0] == tag:
            _, target, parts = self.capture
            target.append(compact_text("".join(parts)))
            self.capture = None


def compact_text(value: str) -> str:
    return " ".join(value.split())


def validate_featured_reviews(
    html: str,
    capabilities: Sequence[WebsiteCapabilitySpec],
) -> list[ValidationIssue]:
    for capability in capabilities:
        if capability.type != "reviews" or not capability.ready:
            continue
        reviews = [
            ReviewData.model_validate(review)
            for review in capability.input_values.get("review_data", [])
        ]
        source = next((review.google_maps_url for review in reviews if review.google_maps_url), None)
        if source is None:
            continue

        markup = ReviewMarkup()
        markup.feed(html)
        markup.close()
        if (
            markup.labels != ["Reseñas destacadas de Google Maps"]
            or markup.links != [source]
            or markup.texts != [compact_text(review.text) for review in reviews]
            or markup.authors != [compact_text(review.author) for review in reviews]
            or markup.ratings != [f"{review.rating} de 5 estrellas" for review in reviews]
        ):
            return [ValidationIssue(
                code="invalid_featured_reviews",
                file="index.html",
                message=(
                    "Integra el bloque de reseñas destacadas completo. Conserva el orden, "
                    "las citas, los autores, las estrellas y el enlace a Google Maps."
                ),
            )]
    return []
