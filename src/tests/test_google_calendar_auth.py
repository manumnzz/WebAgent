from types import SimpleNamespace
from unittest.mock import Mock, sentinel

import pytest
from google.auth.exceptions import RefreshError, TransportError

from integrations import google_calendar_auth as auth


@pytest.fixture
def oauth_environment(tmp_path, monkeypatch):
    credentials_file = tmp_path / "credentials.json"
    token_file = tmp_path / "token.json"

    credentials_file.write_text("{}", encoding="utf-8")
    token_file.write_text("old-token", encoding="utf-8")

    credentials = Mock()
    credentials.valid = False
    credentials.expired = True
    credentials.refresh_token = "fake-refresh-token"
    credentials.to_json.return_value = "refreshed-token"

    new_credentials = Mock()
    new_credentials.valid = True
    new_credentials.to_json.return_value = "new-token"

    loader = Mock(return_value=credentials)

    monkeypatch.setattr(
        auth.Credentials,
        "from_authorized_user_file",
        loader,
    )

    request = Mock(return_value=sentinel.request)
    monkeypatch.setattr(auth, "Request", request)

    flow = Mock()
    flow.run_local_server.return_value = new_credentials

    flow_factory = Mock(return_value=flow)

    monkeypatch.setattr(
        auth.InstalledAppFlow,
        "from_client_secrets_file",
        flow_factory,
    )

    service_builder = Mock(return_value=sentinel.calendar)

    monkeypatch.setattr(
        auth,
        "build",
        service_builder,
    )

    def connect():
        return auth.build_google_calendar_service(
            credentials_path=str(credentials_file),
            token_path=str(token_file),
        )

    return SimpleNamespace(
        credentials=credentials,
        new_credentials=new_credentials,
        token_file=token_file,
        loader=loader,
        request=request,
        flow=flow,
        flow_factory=flow_factory,
        service_builder=service_builder,
        connect=connect,
    )


def test_valid_token_is_reused(oauth_environment):
    env = oauth_environment
    env.credentials.valid = True

    service = env.connect()

    assert service is sentinel.calendar
    env.credentials.refresh.assert_not_called()
    env.flow_factory.assert_not_called()
    env.request.assert_not_called()

    assert env.token_file.read_text(
        encoding="utf-8",
    ) == "old-token"

    env.service_builder.assert_called_once_with(
        "calendar",
        "v3",
        credentials=env.credentials,
    )


def test_expired_token_is_refreshed(oauth_environment):
    env = oauth_environment

    def refresh_successfully(request):
        env.credentials.valid = True

    env.credentials.refresh.side_effect = refresh_successfully

    env.connect()

    env.credentials.refresh.assert_called_once_with(
        sentinel.request,
    )
    env.flow_factory.assert_not_called()

    assert env.token_file.read_text(
        encoding="utf-8",
    ) == "refreshed-token"

    env.service_builder.assert_called_once_with(
        "calendar",
        "v3",
        credentials=env.credentials,
    )


def test_invalid_grant_requests_new_authorization(
    oauth_environment,
):
    env = oauth_environment

    env.credentials.refresh.side_effect = RefreshError(
        "Token expired or revoked.",
        {"error": "invalid_grant"},
    )

    env.connect()

    env.flow_factory.assert_called_once()
    env.flow.run_local_server.assert_called_once_with(port=0)

    assert env.token_file.read_text(
        encoding="utf-8",
    ) == "new-token"

    env.service_builder.assert_called_once_with(
        "calendar",
        "v3",
        credentials=env.new_credentials,
    )


@pytest.mark.parametrize(
    "error",
    [
        RefreshError(
            "Client rejected.",
            {"error": "invalid_client"},
        ),
        RefreshError(
            "Temporary failure.",
            {"error": "invalid_grant"},
            retryable=True,
        ),
        TransportError("Network unavailable."),
    ],
)
def test_other_refresh_errors_are_propagated(
    oauth_environment,
    error,
):
    env = oauth_environment
    env.credentials.refresh.side_effect = error

    with pytest.raises(type(error)) as captured:
        env.connect()

    assert captured.value is error
    env.flow_factory.assert_not_called()
    env.service_builder.assert_not_called()

    assert env.token_file.read_text(
        encoding="utf-8",
    ) == "old-token"


def test_missing_token_requests_authorization(
    oauth_environment,
):
    env = oauth_environment
    env.token_file.unlink()

    env.connect()

    env.loader.assert_not_called()
    env.credentials.refresh.assert_not_called()
    env.flow.run_local_server.assert_called_once_with(port=0)

    assert env.token_file.read_text(
        encoding="utf-8",
    ) == "new-token"


def test_failed_reauthorization_preserves_existing_token(
    oauth_environment,
):
    env = oauth_environment

    env.credentials.refresh.side_effect = RefreshError(
        "Token revoked.",
        {"error": "invalid_grant"},
    )

    env.flow.run_local_server.side_effect = RuntimeError(
        "Authorization cancelled.",
    )

    with pytest.raises(
        RuntimeError,
        match="Authorization cancelled",
    ):
        env.connect()

    env.service_builder.assert_not_called()

    assert env.token_file.read_text(
        encoding="utf-8",
    ) == "old-token"