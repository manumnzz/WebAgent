from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

from fastapi.responses import FileResponse

from capabilities.booking.booking_manager import (
    BookingConfirmation,
    BookingManager,
    BookingSlotUnavailableError,
)
from capabilities.models.booking import (
    BookingRequest,
)
from capabilities.models.booking import (
    BookingRequest,
    BookingService,
)


class AvailabilityResponse(BaseModel):
    booking_date: date
    service_id: str
    available_slots: list[str]


def create_booking_app(
    manager: BookingManager,
) -> FastAPI:

    app = FastAPI(
        title="WebAgent Booking API",
        version="0.1.0",
    )

    static_path = (
        Path(__file__).resolve().parent
        / "static"
    )


    @app.get(
        "/reservar",
        response_class=FileResponse,
    )
    def booking_page():

        return FileResponse(
            static_path / "booking.html"
        )

    @app.get(
        "/booking/availability",
        response_model=AvailabilityResponse,
    )
    def get_availability(
        booking_date: date,
        service_id: str,
    ) -> AvailabilityResponse:

        try:
            slots = manager.get_available_slots(
                booking_date=booking_date,
                service_id=service_id,
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        return AvailabilityResponse(
            booking_date=booking_date,
            service_id=service_id,
            available_slots=[
                slot.strftime("%H:%M")
                for slot in slots
            ],
        )

    @app.post(
        "/booking",
        response_model=BookingConfirmation,
        status_code=201,
    )
    def create_booking(
        request: BookingRequest,
    ) -> BookingConfirmation:

        try:
            return manager.create_booking(
                request
            )

        except BookingSlotUnavailableError as exc:
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc
    @app.get(
        "/booking/services",
        response_model=list[BookingService],
    )
    def get_services() -> list[BookingService]:

        return manager.configuration.services
    return app