import json
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from capabilities.reviews.google_business_profile import fetch_all_reviews
from capabilities.reviews.selection import load_featured_google_reviews, select_featured_reviews


LOCATION = "accounts/123/locations/456"


def page(payload):
    return Mock(**{"json.return_value": payload})


def google_review(review_id, stars, *, text="", anonymous=False):
    return {
        "reviewId": review_id,
        "starRating": stars,
        "comment": text,
        "createTime": "2026-11-01T10:00:00Z",
        "reviewer": {"displayName": "Cliente", "isAnonymous": anonymous},
        "reviewReply": {"comment": "Respuesta privada al ranking"},
    }


def test_google_reads_every_page_before_selecting_featured_reviews():
    session = Mock()
    session.get.side_effect = [
        page({
            "reviews": [
                google_review("first", "FIVE", text="Bien"),
                google_review("negative", "ONE", text="Una experiencia muy mala."),
            ],
            "totalReviewCount": 3,
            "nextPageToken": "next",
        }),
        page({
            "reviews": [
                google_review(
                    "best", "FIVE", text="Repararon los frenos y explicaron el mantenimiento.",
                    anonymous=True,
                ),
            ],
            "totalReviewCount": 3,
        }),
    ]

    reviews = fetch_all_reviews(session, LOCATION)

    assert len(reviews) == 3
    assert [call.kwargs["params"] for call in session.get.call_args_list] == [
        {"pageSize": 50},
        {"pageSize": 50, "pageToken": "next"},
    ]
    assert session.get.call_args.args == (
        "https://mybusiness.googleapis.com/v4/accounts/123/locations/456/reviews",
    )
    selected = select_featured_reviews(reviews)
    assert [review.review_id for review in selected] == ["best", "first"]
    assert selected[0].author == "Usuario anónimo de Google"
    assert "reviewReply" not in selected[0].model_dump()


@pytest.mark.parametrize("failure", ["incomplete", "cycle"])
def test_google_does_not_return_partial_results(failure):
    payload = {"reviews": [google_review("1", "THREE")], "totalReviewCount": 2}
    if failure == "cycle":
        payload["nextPageToken"] = "repeat"
    session = Mock(**{"get.return_value": page(payload)})

    with pytest.raises(ValueError, match="total de reseñas|repitió una página"):
        fetch_all_reviews(session, LOCATION)


def test_google_rejects_a_location_outside_the_expected_resource():
    session = Mock()
    with pytest.raises(ValueError, match="identificador"):
        fetch_all_reviews(session, "https://example.org")
    session.get.assert_not_called()


def test_import_ranks_by_stars_detail_and_recency_without_rewriting_quotes(tmp_path):
    path = tmp_path / "google_reviews.json"
    source = "https://www.google.com/maps/place/Taller/"
    detailed = "Explicaron los frenos con claridad.\nEl presupuesto estuvo listo el mismo día."
    path.write_text(json.dumps({
        "google_maps_url": source,
        "reviews": [
            {"author": "Sin texto", "rating": 5},
            {"author": "Ana", "text": "Atención excelente", "rating": 5, "published_at": "2026-02-01T10:00:00Z"},
            {"author": "Eli", "text": detailed, "rating": 5},
            {"author": "Yolanda", "text": "Atención excelente", "rating": 5, "published_at": "2026-01-01T10:00:00Z"},
            {"author": "Eli", "text": detailed, "rating": 5},
            {"author": "Luz", "text": "Buena recepción con seguimiento de la reparación y consulta del presupuesto", "rating": 4},
            {"author": "Luis", "text": "Esperé varias horas", "rating": 2},
        ],
    }))

    selected = load_featured_google_reviews(path)

    assert [review.author for review in selected] == ["Eli", "Ana", "Yolanda"]
    assert selected[0].text == detailed
    assert all(review.google_maps_url == source for review in selected)


@pytest.mark.parametrize("url", [
    "javascript:alert(1)",
    "https://www.google.com.ejemplo.org/maps/place/Taller/",
    "https://www.google.com@ejemplo.org/maps/place/Taller/",
])
def test_import_requires_a_valid_google_maps_source(tmp_path, url):
    path = tmp_path / "google_reviews.json"
    path.write_text(json.dumps({"google_maps_url": url, "reviews": []}))
    with pytest.raises(ValidationError, match="enlace HTTPS"):
        load_featured_google_reviews(path)
