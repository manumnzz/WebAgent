
from fastapi.testclient import TestClient

from intake.api import create_intake_app


def make_payload():
    return {
        "business_name": "Fisio de prueba",
        "business_description": "Clínica de fisioterapia.",
        "requested_features": ["booking"],
        "appointment_types": ["Valoración inicial"],
        "booking": {
            "service_durations": {
                "valoracion-inicial": 45,
            },
            "timezone": "Europe/Madrid",
        },
    }


def make_schedule(open_days):
    weekdays = [
        "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday",
    ]

    return [
        {
            "weekday": day,
            "ranges": (
                [{"start": "09:00", "end": "14:00"}]
                if day in open_days
                else []
            ),
        }
        for day in weekdays
    ]


def test_api_rejects_missing_weekdays(tmp_path):
    client = TestClient(create_intake_app(tmp_path))
    payload = make_payload()

    payload["booking"]["weekly_schedule"] = [
        {
            "weekday": "monday",
            "ranges": [
                {"start": "09:00", "end": "14:00"}
            ],
        }
    ]

    response = client.post("/intake", json=payload)

    assert response.status_code == 422
    assert "siete días" in response.json()["detail"]
    assert list(tmp_path.iterdir()) == []


def test_api_rejects_all_days_closed(tmp_path):
    client = TestClient(create_intake_app(tmp_path))
    payload = make_payload()

    payload["booking"]["weekly_schedule"] = make_schedule(
        open_days=set()
    )

    response = client.post("/intake", json=payload)

    assert response.status_code == 422
    assert "al menos un día" in response.json()["detail"]
    assert list(tmp_path.iterdir()) == []


def test_api_accepts_valid_schedule(tmp_path):
    client = TestClient(create_intake_app(tmp_path))
    payload = make_payload()

    payload["booking"]["weekly_schedule"] = make_schedule(
        open_days={"monday", "wednesday"}
    )

    response = client.post("/intake", json=payload)

    assert response.status_code == 201
    assert response.json()["status"] == "received"


def test_api_accepts_inquiry_without_schedule(tmp_path):
    client = TestClient(create_intake_app(tmp_path))
    payload = make_payload()

    payload["appointment_types"] = ["Pedir presupuesto"]
    payload["booking"] = {
        "timezone": "Europe/Madrid"
    }

    response = client.post("/intake", json=payload)

    assert response.status_code == 201


def test_api_accepts_project_without_booking(tmp_path):
    client = TestClient(create_intake_app(tmp_path))
    payload = make_payload()

    payload["requested_features"] = ["maps"]
    payload["booking"] = None

    response = client.post("/intake", json=payload)

    assert response.status_code == 201
