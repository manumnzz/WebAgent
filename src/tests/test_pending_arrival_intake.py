from fastapi.testclient import TestClient

from intake.api import create_intake_app
from intake.loader import load_project_input


def test_saves_pending_arrival_mode_without_repair_duration(tmp_path):
    client = TestClient(create_intake_app(tmp_path))
    response = client.post("/intake", json={
        "business_name": "Taller Prueba",
        "business_description": "Reparación de vehículos.",
        "services": ["Diagnóstico de fallos"],
        "requested_features": ["booking"],
        "appointment_types": ["Entrega del vehículo"],
        "booking": {
            "service_durations": {},
            "appointment_modes": {"entrega-del-vehiculo": "pending_arrival"},
            "timezone": "Europe/Madrid",
        },
    })

    assert response.status_code == 201
    saved = tmp_path / response.json()["submission_id"] / "project_input.json"
    loaded = load_project_input(saved)
    assert loaded.booking.appointment_modes == {
        "entrega-del-vehiculo": "pending_arrival"
    }
