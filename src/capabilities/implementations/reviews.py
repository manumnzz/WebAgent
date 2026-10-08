from html import escape

from capabilities.capability_implementation import (
    CapabilityImplementation,
)

from capabilities.models.review import (
    ReviewData,
)


def build_reviews_implementation(
    review_data: list[ReviewData | dict],
) -> CapabilityImplementation:

    if not review_data:
        raise ValueError(
            "No existen reseñas disponibles."
        )

    reviews = [
        (
            review
            if isinstance(review, ReviewData)
            else ReviewData.model_validate(review)
        )
        for review in review_data
    ]

    review_items = []

    for review in reviews:

        author = escape(
            review.author.strip()
        )

        text = escape(
            review.text.strip()
        )

        if not author or not text:
            raise ValueError(
                "Las reseñas deben incluir autor y contenido."
            )

        stars = (
            "★" * review.rating
            + "☆" * (5 - review.rating)
        )

        review_items.append(
            f"""
<article class="capability-review">
    <div
        class="capability-review-rating"
        aria-label="{review.rating} de 5 estrellas"
    >
        {stars}
    </div>

    <blockquote class="capability-review-text">
        {text}
    </blockquote>

    <p class="capability-review-author">
        {author}
    </p>
</article>
""".strip()
        )

    items_html = "\n".join(
        review_items
    )

    html = f"""
<div class="capability-reviews">
    {items_html}
</div>
""".strip()

    return CapabilityImplementation(
        type="reviews",
        html=html,
        css="",
        javascript="",
        implementation_notes=[
            (
                f"Se han integrado "
                f"{len(reviews)} reseña(s) reales."
            )
        ],
    )