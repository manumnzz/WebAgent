from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.freebusy",
]


def _requires_new_authorization(error: RefreshError) -> bool:
    if error.retryable:
        return False

    return any(
        isinstance(detail, dict)
        and detail.get("error") == "invalid_grant"
        for detail in error.args
    )


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

    if credentials is None or not credentials.valid:
        can_refresh = (
            credentials is not None
            and credentials.expired
            and credentials.refresh_token
        )

        if can_refresh:
            try:
                credentials.refresh(Request())

            except RefreshError as error:
                if not _requires_new_authorization(error):
                    raise

                print(
                    "Google ha rechazado la renovación del token. "
                    "Se solicitará una nueva autorización."
                )

                credentials = None

        if credentials is None or not credentials.valid:
            if not credentials_file.exists():
                raise FileNotFoundError(
                    f"No existe el archivo "
                    f"'{credentials_path}'."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file,
                SCOPES,
            )

            credentials = flow.run_local_server(port=0)

        token_file.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )