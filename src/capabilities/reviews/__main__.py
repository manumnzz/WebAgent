import argparse
from collections import Counter
from pathlib import Path

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2 import OAuth2Error
from requests import RequestException

from capabilities.reviews.google_business_profile import (
    BUSINESS_SCOPE,
    fetch_all_reviews,
    validate_location,
)
from capabilities.reviews.selection import detail_score, select_featured_reviews


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audita y clasifica en memoria las reseñas de una ficha de Google Business Profile.",
    )
    parser.add_argument("--location", required=True, help="accounts/ID/locations/ID de Google.")
    parser.add_argument("--client-secrets", required=True, type=Path, help="Cliente OAuth de escritorio.")
    args = parser.parse_args()

    try:
        location = validate_location(args.location)
        flow = InstalledAppFlow.from_client_secrets_file(
            str(args.client_secrets), scopes=[BUSINESS_SCOPE],
        )
        credentials = flow.run_local_server(
            host="localhost", port=0, timeout_seconds=180, access_type="online",
        )
        with AuthorizedSession(credentials) as session:
            reviews = fetch_all_reviews(session, location)
    except RequestException as error:
        status = error.response.status_code if error.response is not None else "sin respuesta HTTP"
        parser.exit(1, f"No se pudo completar la consulta a Google ({status}).\n")
    except (GoogleAuthError, OAuth2Error):
        parser.exit(1, "Google no autorizó el acceso al Perfil de Empresa.\n")
    except (OSError, ValueError) as error:
        parser.exit(1, f"No se pudo completar la consulta a Google. {error}\n")

    counts = Counter(review.rating for review in reviews)
    print(f"Reseñas evaluadas: {len(reviews)}")
    for rating in range(5, 0, -1):
        print(f"{rating} estrellas: {counts[rating]}")
    for review in select_featured_reviews(reviews):
        print(f"Candidata {review.review_id}: {review.rating}/5, detalle {detail_score(review.text)}")


if __name__ == "__main__":
    main()
