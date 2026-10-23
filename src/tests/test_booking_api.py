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
    PendingArrivalType,
    InquiryType,
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


def test_pending_arrival_is_visible_but_does_not_block_confirmed_booking():
    manager, provider = build_manager()
    manager.configuration.pending_arrival_types = [
        PendingArrivalType(id="car-dropoff", name="Entrega del vehículo")
    ]
    client = TestClient(create_booking_app(manager))

    options = client.get("/booking/options")
    assert options.status_code == 200
    assert options.json()[-1] == {
        "id": "car-dropoff", "name": "Entrega del vehículo",
        "mode": "pending", "duration_minutes": None,
    }
    arrival_slots = client.get("/booking/request-availability", params={
        "booking_date": "2030-01-04", "service_id": "car-dropoff",
    })
    assert "11:00" in arrival_slots.json()["available_slots"]

    pending = client.post("/booking/requests", json={
        "first_name": "Manuel", "last_name": "Buzón",
        "phone": "600123123", "service_id": "car-dropoff",
        "booking_date": "2030-01-04", "booking_time": "11:00",
        "notes": "El coche no arranca.",
    })
    assert pending.status_code == 201
    assert pending.json()["status"] == "pending"
    assert len(provider.pending_events) == 1
    assert provider.busy_intervals == []

    confirmed = client.post("/booking", json={
        "first_name": "Ana", "last_name": "Pérez",
        "phone": "600222333", "service_id": "haircut",
        "booking_date": "2030-01-04", "booking_time": "11:00",
    })
    assert confirmed.status_code == 201


def test_pending_arrival_needs_reason_and_valid_working_hour():
    manager, provider = build_manager()
    manager.configuration.pending_arrival_types = [
        PendingArrivalType(id="car-dropoff", name="Entrega del vehículo")
    ]
    client = TestClient(create_booking_app(manager))
    request = {
        "first_name": "Manuel", "last_name": "Buzón",
        "phone": "600123123", "service_id": "car-dropoff",
        "booking_date": "2030-01-04", "booking_time": "11:00",
    }
    assert client.post("/booking/requests", json=request).status_code == 422
    assert client.post("/booking/requests", json={
        **request, "notes": "Avería", "booking_time": "18:00",
    }).status_code == 409
    assert provider.pending_events == {}


def test_inquiry_without_a_time_is_recorded_without_blocking_calendar():
    manager, provider = build_manager()
    manager.configuration.inquiry_types = [
        InquiryType(id="quote", name="Pedir presupuesto")
    ]
    client = TestClient(create_booking_app(manager))
    assert client.get("/booking/options").json()[-1]["mode"] == "inquiry"

    response = client.post("/booking/inquiries", json={
        "first_name": "Manuel", "last_name": "Buzón",
        "email": "manuel@example.com", "service_id": "quote",
        "notes": "Quiero presupuestar un cambio de suspensión.",
    })
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert len(provider.inquiry_events) == 1
    assert provider.busy_intervals == []
