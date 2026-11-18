import re

from google.auth.transport.requests import AuthorizedSession
from pydantic import AwareDatetime, BaseModel, Field, ValidationError

from capabilities.reviews.selection import ReviewCandidate


BUSINESS_SCOPE = "https://www.googleapis.com/auth/business.manage"
RATINGS = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}


class Reviewer(BaseModel):
    displayName: str | None = None
    isAnonymous: bool = False


class GoogleReview(BaseModel):
    reviewId: str = Field(min_length=1)
    starRating: str
    comment: str = ""
    createTime: AwareDatetime | None = None
    reviewer: Reviewer = Field(default_factory=Reviewer)

    def as_candidate(self) -> ReviewCandidate:
        if self.starRating not in RATINGS:
            raise ValueError("Google devolvió una valoración sin un número de estrellas válido.")
        author = None if self.reviewer.isAnonymous else self.reviewer.displayName
        return ReviewCandidate(
            review_id=self.reviewId,
            author=(author or "").strip() or "Usuario anónimo de Google",
            text=self.comment,
            rating=RATINGS[self.starRating],
            published_at=self.createTime,
        )


class ReviewPage(BaseModel):
    reviews: list[GoogleReview] = Field(default_factory=list)
    totalReviewCount: int | None = Field(default=None, ge=0)
    nextPageToken: str = ""


def validate_location(location: str) -> str:
    if not re.fullmatch(r"accounts/[0-9]+/locations/[0-9]+", location):
        raise ValueError("Usa el identificador accounts/ID/locations/ID de la ficha verificada.")
    return location


def fetch_all_reviews(session: AuthorizedSession, location: str) -> list[ReviewCandidate]:
    url = f"https://mybusiness.googleapis.com/v4/{validate_location(location)}/reviews"
    candidates: dict[str, ReviewCandidate] = {}
    received_tokens = set()
    expected_counts = set()
    params = {"pageSize": 50}

    while True:
        response = session.get(url, params=params, timeout=20)
        response.raise_for_status()
        try:
            page = ReviewPage.model_validate(response.json())
        except ValidationError:
            raise ValueError("Google devolvió una página de reseñas con formato inesperado.") from None
        if page.totalReviewCount is not None:
            expected_counts.add(page.totalReviewCount)
        for review in page.reviews:
            candidates[review.reviewId] = review.as_candidate()

        token = page.nextPageToken
        if not token:
            break
        if token in received_tokens:
            raise ValueError("Google repitió una página de reseñas. Repite la consulta.")
        received_tokens.add(token)
        params = {"pageSize": 50, "pageToken": token}

    if expected_counts and expected_counts != {len(candidates)}:
        raise ValueError("El total de reseñas cambió durante la consulta. Repite la consulta.")

    return list(candidates.values())
