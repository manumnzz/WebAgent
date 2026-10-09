from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]


def build_google_calendar_service(
    credentials_path: str = "credentials.json",
    token_path: str = "token.json",
):

    credentials_file = Path(credentials_path)
    token_file = Path(token_path)

    credentials = None

    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            token_file,
            SCOPES,
        )

    if (
        not credentials
        or not credentials.valid
    ):

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(
                Request()
            )

        else:
            if not credentials_file.exists():
                raise FileNotFoundError(
                    f"No existe el archivo "
                    f"'{credentials_path}'."
                )

            flow = (
                InstalledAppFlow
                .from_client_secrets_file(
                    credentials_file,
                    SCOPES,
                )
            )

            credentials = (
                flow.run_local_server(
                    port=0
                )
            )

        token_file.write_text(
            credentials.to_json()
        )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )