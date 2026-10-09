from datetime import time

from fastapi.testclient import TestClient

from api.booking_api import (
    create_booking_app,
)
from capabilities.booking.booking_manager import (
    BookingManager,
)
from capabilities.booking.fake_calendar_provider import (
    FakeCalendarProvider,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingDaySchedule,
    BookingService,
    BookingTimeRange,
)


def build_manager():

    configuration = BookingConfiguration(
        timezone="Europe/Madrid",
        services=[
            BookingService(
                id="haircut",
                name="Corte",
                duration_minutes=30,
            ),
            BookingService(
                id="cut_beard",
                name="Corte + barba",
                duration_minutes=45,
            ),
        ],
        weekly_schedule=[
            BookingDaySchedule(
                weekday="friday",
                ranges=[
                    BookingTimeRange(
                        start=time(9, 0),
                        end=time(14, 0),
                    )
                ],
            )
        ],
        slot_interval_minutes=30,
    )

    provider = FakeCalendarProvider()

    return (
        BookingManager(
            configuration=configuration,
            calendar_provider=provider,
        ),
        provider,
    )


def test_get_booking_availability():

    manager, _ = build_manager()

    app = create_booking_app(
        manager
    )

    client = TestClient(app)

    response = client.get(
        "/booking/availability",
        params={
            "booking_date": "2026-10-16",
            "service_id": "haircut",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["service_id"] == "haircut"

    assert data["available_slots"] == [
        "09:00",
        "09:30",
        "10:00",
        "10:30",
        "11:00",
        "11:30",
        "12:00",
        "12:30",
        "13:00",
        "13:30",
    ]


def test_create_booking():

    manager, provider = build_manager()

    app = create_booking_app(
        manager
    )

    client = TestClient(app)

    response = client.post(
        "/booking",
        json={
            "first_name": "Manuel",
            "last_name": "Buzón",
            "email": "manuel@example.com",
            "service_id": "haircut",
            "booking_date": "2026-10-16",
            "booking_time": "11:00:00",
            "notes": "Degradado bajo.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["service_id"] == "haircut"
    assert data["service_name"] == "Corte"

    assert len(
        provider.created_events
    ) == 1


def test_api_prevents_double_booking():

    manager, _ = build_manager()

    app = create_booking_app(
        manager
    )

    client = TestClient(app)

    booking = {
        "first_name": "Manuel",
        "last_name": "Buzón",
        "email": "manuel@example.com",
        "service_id": "haircut",
        "booking_date": "2026-10-16",
        "booking_time": "11:00:00",
    }

    first_response = client.post(
        "/booking",
        json=booking,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/booking",
        json={
            **booking,
            "first_name": "Carlos",
            "last_name": "Pérez",
            "email": "carlos@example.com",
        },
    )

    assert second_response.status_code == 409

    assert (
        second_response.json()["detail"]
        == "El horario solicitado ya no está disponible."
    )


def test_unknown_service_returns_400():

    manager, _ = build_manager()

    app = create_booking_app(
        manager
    )

    client = TestClient(app)

    response = client.get(
        "/booking/availability",
        params={
            "booking_date": "2026-10-16",
            "service_id": "does_not_exist",
        },
    )

    assert response.status_code == 400

def test_get_booking_services():

    manager, _ = build_manager()

    app = create_booking_app(
        manager
    )

    client = TestClient(app)

    response = client.get(
        "/booking/services"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0] == {
        "id": "haircut",
        "name": "Corte",
        "duration_minutes": 30,
    }