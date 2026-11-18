import re
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from capabilities.models.review import GoogleMapsURL, ReviewData


FEATURED_LIMIT = 3
MINIMUM_RATING = 4


class ReviewCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    author: str = Field(min_length=1)
    text: str = ""
    rating: int = Field(ge=1, le=5, strict=True)
    review_id: str | None = None
    published_at: AwareDatetime | None = None


class GoogleReviewsFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    google_maps_url: GoogleMapsURL
    reviews: list[ReviewCandidate]


def detail_score(text: str) -> int:
    words = re.findall(r"[^\W\d_]+", text.casefold())
    return min(45, len({word for word in words if len(word) >= 4}))


def select_featured_reviews(reviews: Iterable[ReviewCandidate]) -> list[ReviewCandidate]:
    """Prefer higher ratings, specific comments and then more recent experiences."""
    candidates = [
        review for review in reviews
        if review.rating >= MINIMUM_RATING and any(character.isalnum() for character in review.text)
    ]
    candidates.sort(
        key=lambda review: (
            review.rating,
            detail_score(review.text),
            review.published_at or datetime.min.replace(tzinfo=UTC),
            review.author.casefold(),
            review.text.casefold(),
            review.review_id or "",
        ),
        reverse=True,
    )

    selected = []
    seen_quotes = set()
    seen_ids = set()
    for review in candidates:
        quote = (review.author.casefold(), " ".join(review.text.casefold().split()))
        if quote in seen_quotes or review.review_id in seen_ids:
            continue
        seen_quotes.add(quote)
        if review.review_id:
            seen_ids.add(review.review_id)
        selected.append(review)
        if len(selected) == FEATURED_LIMIT:
            break

    return selected


def load_featured_google_reviews(path: Path) -> list[ReviewData]:
    source = GoogleReviewsFile.model_validate_json(path.read_bytes())
    return [
        ReviewData(
            author=review.author,
            text=review.text,
            rating=review.rating,
            google_maps_url=source.google_maps_url,
        )
        for review in select_featured_reviews(source.reviews)
    ]
