from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from capabilities.booking.booking_manager import (
    BookingConfirmation,
    BookingManager,
    BookingSlotUnavailableError,
    InquiryConfirmation,
    PendingArrivalConfirmation,
)
from capabilities.models.booking import (
    BookingRequest,
    BookingService,
    InquiryRequest,
    PendingArrivalRequest,
)
from tools.filesystem_tools import WEBSITE_ROOT


class AvailabilityResponse(BaseModel):
    booking_date: date
    service_id: str
    available_slots: list[str]


class AppointmentOption(BaseModel):
    id: str
    name: str
    mode: str
    duration_minutes: int | None = None


def create_booking_app(
    manager: BookingManager,
    *,
    website_root: Path | None = WEBSITE_ROOT,
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

    @app.get(
        "/booking/request-availability",
        response_model=AvailabilityResponse,
    )
    def get_request_availability(
        booking_date: date,
        service_id: str,
    ) -> AvailabilityResponse:
        try:
            slots = manager.get_available_arrival_slots(
                booking_date=booking_date,
                option_id=service_id,
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
            return manager.create_booking(request)

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

    @app.post(
        "/booking/requests",
        response_model=PendingArrivalConfirmation,
        status_code=201,
    )
    def create_pending_arrival(
        request: PendingArrivalRequest,
    ) -> PendingArrivalConfirmation:
        try:
            return manager.create_pending_arrival(request)

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

    @app.post(
        "/booking/inquiries",
        response_model=InquiryConfirmation,
        status_code=201,
    )
    def create_inquiry(
        request: InquiryRequest,
    ) -> InquiryConfirmation:
        try:
            return manager.create_inquiry(request)

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

    @app.get(
        "/booking/options",
        response_model=list[AppointmentOption],
    )
    def get_appointment_options() -> list[AppointmentOption]:
        confirmed = [
            AppointmentOption(
                id=service.id,
                name=service.name,
                mode="confirmed",
                duration_minutes=service.duration_minutes,
            )
            for service in manager.configuration.services
        ]

        pending = [
            AppointmentOption(
                id=option.id,
                name=option.name,
                mode="pending",
            )
            for option in manager.configuration.pending_arrival_types
        ]

        inquiries = [
            AppointmentOption(
                id=option.id,
                name=option.name,
                mode="inquiry",
            )
            for option in manager.configuration.inquiry_types
        ]

        return confirmed + pending + inquiries

    if website_root is not None:
        app.mount(
            "/",
            StaticFiles(
                directory=website_root,
                html=True,
            ),
            name="generated-website",
        )

    return app
