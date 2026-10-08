import pytest
from pydantic import ValidationError

from capabilities.implementations.reviews import (
    build_reviews_implementation,
)

from capabilities.models.review import (
    ReviewData,
)


def test_reviews_capability():

    implementation = build_reviews_implementation(
        review_data=[
            ReviewData(
                author="Carlos",
                text="Trabajo impecable.",
                rating=5,
            ),
            ReviewData(
                author="Laura",
                text="Muy buen trato.",
                rating=4,
            ),
        ]
    )

    assert implementation.type == "reviews"

    assert "Carlos" in implementation.html
    assert "Laura" in implementation.html

    assert "Trabajo impecable." in implementation.html

    assert (
        implementation.html.count(
            'class="capability-review"'
        )
        == 2
    )

    assert "★★★★★" in implementation.html
    assert "★★★★☆" in implementation.html


def test_reviews_accept_dict_data():

    implementation = build_reviews_implementation(
        review_data=[
            {
                "author": "Carlos",
                "text": "Muy recomendable.",
                "rating": 5,
            }
        ]
    )

    assert "Carlos" in implementation.html
    assert "Muy recomendable." in implementation.html


def test_reviews_reject_empty_list():

    with pytest.raises(ValueError):

        build_reviews_implementation(
            review_data=[]
        )


def test_review_rejects_invalid_rating():

    with pytest.raises(ValidationError):

        ReviewData(
            author="Carlos",
            text="Buen servicio.",
            rating=6,
        )