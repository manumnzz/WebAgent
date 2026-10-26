from fastapi.testclient import TestClient

from api import main as project_api
from projects.workspace import build_project_workspace

from capabilities.booking.config_writer import (
    save_booking_configuration,
)
from capabilities.booking.fake_calendar_provider import (
    FakeCalendarProvider,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingService,
)

def test_two_apps_serve_independent_projects(
    tmp_path,
    monkeypatch,
):
    def build_test_workspace(project_id):
        return build_project_workspace(
            project_id,
            projects_directory=tmp_path,
        )

    monkeypatch.setattr(
        project_api,
        "build_project_workspace",
        build_test_workspace,
    )

    def unexpected_google_connection(**kwargs):
        raise AssertionError(
            "Una web sin Booking no debe conectar con Google."
        )

    monkeypatch.setattr(
        project_api,
        "build_google_calendar_service",
        unexpected_google_connection,
    )

    clients = {}

    for project_id, content in [
        ("fisio", "<h1>Fisio Alameda</h1>"),
        ("taller", "<h1>Iron Garage</h1>"),
    ]:
        workspace = build_test_workspace(project_id)
        workspace.create_directories()

        (workspace.website_directory / "index.html").write_text(
            content,
            encoding="utf-8",
        )

        monkeypatch.setenv(
            "WEBAGENT_PROJECT_ID",
            project_id,
        )

        clients[project_id] = TestClient(
            project_api.create_project_app()
        )

    with clients["fisio"] as fisio, clients["taller"] as taller:
        fisio_response = fisio.get("/")
        taller_response = taller.get("/")

        assert fisio_response.status_code == 200
        assert taller_response.status_code == 200

        assert fisio_response.text == "<h1>Fisio Alameda</h1>"
        assert taller_response.text == "<h1>Iron Garage</h1>"

        assert fisio.get("/health").json() == {
            "status": "ok",
            "project_id": "fisio",
            "booking_enabled": False,
        }

        assert taller.get("/health").json() == {
            "status": "ok",
            "project_id": "taller",
            "booking_enabled": False,
        }

def test_two_apps_load_independent_booking_configurations(
    tmp_path,
    monkeypatch,
):
    def build_test_workspace(project_id):
        return build_project_workspace(
            project_id,
            projects_directory=tmp_path,
        )

    monkeypatch.setattr(
        project_api,
        "build_project_workspace",
        build_test_workspace,
    )

    # Sustituir la conexión externa a Google.
    monkeypatch.setattr(
        project_api,
        "build_google_calendar_service",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        project_api,
        "GoogleCalendarProvider",
        lambda **kwargs: FakeCalendarProvider(),
    )

    clients = {}

    projects = [
        ("fisio", "fisioterapia", "Fisioterapia", 45),
        ("taller", "aceite", "Cambio de aceite", 60),
    ]

    for project_id, service_id, service_name, duration in projects:
        workspace = build_test_workspace(project_id)
        workspace.create_directories()

        (workspace.website_directory / "index.html").write_text(
            f"<h1>{project_id}</h1>",
            encoding="utf-8",
        )

        configuration = BookingConfiguration(
            timezone="Europe/Madrid",
            services=[
                BookingService(
                    id=service_id,
                    name=service_name,
                    duration_minutes=duration,
                ),
            ],
        )

        save_booking_configuration(
            configuration,
            path=workspace.booking_configuration_path,
        )

        monkeypatch.setenv(
            "WEBAGENT_PROJECT_ID",
            project_id,
        )

        clients[project_id] = TestClient(
            project_api.create_project_app()
        )

    with clients["fisio"] as fisio, clients["taller"] as taller:
        for client, expected_project in [
            (fisio, "fisio"),
            (taller, "taller"),
        ]:
            response = client.get("/health")

            assert response.status_code == 200
            assert response.json() == {
                "status": "ok",
                "project_id": expected_project,
                "booking_enabled": True,
            }

        fisio_services = fisio.get("/booking/services")
        taller_services = taller.get("/booking/services")

        assert fisio_services.status_code == 200
        assert taller_services.status_code == 200

        assert fisio_services.json() == [
            {
                "id": "fisioterapia",
                "name": "Fisioterapia",
                "duration_minutes": 45,
            },
        ]

        assert taller_services.json() == [
            {
                "id": "aceite",
                "name": "Cambio de aceite",
                "duration_minutes": 60,
            },
        ]

        # La configuración interna no debe publicarse con la web.
        assert fisio.get("/config/booking.json").status_code == 404
        assert taller.get("/config/booking.json").status_code == 404