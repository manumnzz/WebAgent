import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.booking_api import create_booking_app
from capabilities.booking.booking_manager import BookingManager
from capabilities.booking.config_loader import (
    load_booking_configuration,
)
from capabilities.booking.google_calendar_provider import (
    GoogleCalendarProvider,
)
from integrations.google_calendar_auth import (
    build_google_calendar_service,
)
from projects.workspace import (
    PROJECT_ROOT,
    build_project_workspace,
)


load_dotenv()


def create_project_app() -> FastAPI:
    # 1. Seleccionar el proyecto.
    project_id = os.getenv("WEBAGENT_PROJECT_ID")

    if not project_id:
        raise ValueError(
            "Debes indicar WEBAGENT_PROJECT_ID "
            "para seleccionar el proyecto."
        )

    workspace = build_project_workspace(project_id)

    # 2. Comprobar que tiene una web generada.
    index_path = workspace.website_directory / "index.html"

    if not index_path.is_file():
        raise FileNotFoundError(
            f"No existe una web generada para '{project_id}': "
            f"{index_path}"
        )

    # 3. Comprobar si tiene configuración de Booking.
    booking_enabled = (
        workspace.booking_configuration_path.is_file()
    )

    if booking_enabled:
        configuration = load_booking_configuration(
            workspace.booking_configuration_path,
        )

        google_service = build_google_calendar_service(
            credentials_path=str(
                PROJECT_ROOT / "credentials.json"
            ),
            token_path=str(
                PROJECT_ROOT / "token.json"
            ),
        )

        calendar_provider = GoogleCalendarProvider(
            service=google_service,
            business_info=configuration.business,
        )

        booking_manager = BookingManager(
            configuration=configuration,
            calendar_provider=calendar_provider,
        )

        # Crear las rutas de Booking sin montar todavía la web.
        app = create_booking_app(
            booking_manager,
            website_root=None,
        )

    else:
        # Sin Booking no necesitamos iniciar Google Calendar.
        app = FastAPI(
            title="WebAgent Website",
            version="0.1.0",
        )

    # 4. Añadir una ruta para comprobar el proyecto seleccionado.
    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "project_id": workspace.project_id,
            "booking_enabled": booking_enabled,
        }

    # 5. Montar la web después de registrar las rutas de la API.
    app.mount(
        "/",
        StaticFiles(
            directory=workspace.website_directory,
            html=True,
        ),
        name="generated-website",
    )

    return app