from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from intake.models import ProjectInput
from intake.booking_adapter import build_booking_draft_from_input
from intake.storage import save_project_input

from capabilities.booking.configuration_builder import (
    build_booking_service_drafts,
)
from capabilities.models.booking import BookingServiceDraft


PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRONTEND_DIRECTORY = (
    Path(__file__).resolve().parent / "frontend"
)


class IntakeReceipt(BaseModel):
    submission_id: str
    status: str

class BookingServiceInput(BaseModel):
    services: list[str]

def create_intake_app(
    storage_directory: str | Path | None = None,
) -> FastAPI:
    app = FastAPI(
        title="WebAgent — Recepción de encargos"
    )

    storage_path = (
        Path(storage_directory)
        if storage_directory is not None
        else PROJECT_ROOT / "data" / "intake"
    )

    @app.get("/", response_class=FileResponse)
    def show_form() -> FileResponse:
        return FileResponse(
            FRONTEND_DIRECTORY / "index.html"
        )

    @app.post(
        "/intake",
        response_model=IntakeReceipt,
        status_code=201,
    )
    def receive_project(
        project_input: ProjectInput,
    ) -> IntakeReceipt:
        try:
            build_booking_draft_from_input(project_input)
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        try:
            submission_id = save_project_input(
                project_input,
                storage_path,
            )
        except OSError as error:
            raise HTTPException(
                status_code=500,
                detail=(
                    "No se ha podido guardar el encargo. "
                    "Inténtalo de nuevo."
                ),
            ) from error

        return IntakeReceipt(
            submission_id=submission_id,
            status="received",
        )

    @app.post(
        "/intake/booking-services",
        response_model=list[BookingServiceDraft],
    )
    def prepare_booking_services(
        payload: BookingServiceInput,
    ) -> list[BookingServiceDraft]:
        try:
            return build_booking_service_drafts(
                payload.services
            )
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

    return app


app = create_intake_app()
