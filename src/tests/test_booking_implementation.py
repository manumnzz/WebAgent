import pytest

from capabilities.implementations.booking import (
    build_booking_implementation,
)


def build_booking_configuration():
    return {
        "timezone": "Europe/Madrid",
        "services": [
            {
                "id": "corte",
                "name": "Corte",
                "duration_minutes": 30,
            }
        ],
        "weekly_schedule": [
            {
                "weekday": "monday",
                "ranges": [
                    {
                        "start": "09:00",
                        "end": "14:00",
                    }
                ],
            }
        ],
        "slot_interval_minutes": 30,
    }


def test_build_booking_implementation():

    implementation = build_booking_implementation(
        build_booking_configuration()
    )

    assert implementation.type == "booking"

    assert 'href="/reservar"' in implementation.html

    assert "Ver citas y solicitudes" in implementation.html


def test_booking_implementation_has_no_calendar_logic():

    implementation = build_booking_implementation(
        build_booking_configuration()
    )

    assert "google" not in implementation.javascript.lower()
    assert "calendar" not in implementation.javascript.lower()


def test_inquiry_provides_direct_link_to_its_option():
    configuration = build_booking_configuration()
    configuration["inquiry_types"] = [
        {"id": "pedir-presupuesto", "name": "Pedir presupuesto"}
    ]

    implementation = build_booking_implementation(configuration)

    assert 'href="/reservar?service_id=pedir-presupuesto"' in implementation.html
    assert "Pedir presupuesto" in implementation.html
    assert "mailto:" not in implementation.html


def test_booking_implementation_requires_services():

    configuration = build_booking_configuration()

    configuration["services"] = []

    with pytest.raises(ValueError):
        build_booking_implementation(
            configuration
        )
