import pytest

from capabilities.booking.configuration_finalizer import (
    finalize_booking_configuration,
)
from capabilities.booking.configuration_readiness import (
    get_booking_missing_information,
)
from intake.booking_adapter import (
    build_booking_draft_from_input,
    get_request_only_appointments,
)
from intake.models import ProjectInput


def make_project_input(**overrides) -> ProjectInput:
    data = {
        "business_name": "Fisio de prueba",
        "business_description": "Negocio ficticio para tests.",
        "services": ["Valoración inicial"],
        "requested_features": ["booking"],
        "appointment_types": ["Valoración inicial"],
    }

    data.update(overrides)

    return ProjectInput.model_validate(data)


def test_does_not_build_booking_when_not_requested():
    project_input = make_project_input(
        requested_features=["maps"],
        booking={"timezone": "Europe/Madrid"},
    )

    draft = build_booking_draft_from_input(
        project_input,
    )

    assert draft is None


def test_legacy_appointment_without_duration_remains_an_inquiry():
    project_input = make_project_input(
        booking={"timezone": "Europe/Madrid"},
    )

    draft = build_booking_draft_from_input(
        project_input,
        
    )

    assert draft is not None
    assert draft.services == []
    assert draft.pending_arrival_types == []
    assert draft.inquiry_types[0].id == "valoracion-inicial"
    assert get_request_only_appointments(project_input) == ["Valoración inicial"]


def test_applies_confirmed_conditions_without_fixed_values():
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    project_input = make_project_input(
        booking={
            "service_durations": {
                "valoracion-inicial": 45,
            },
            "timezone": "Atlantic/Canary",
            "slot_interval_minutes": 15,
            "weekly_schedule": [
                {
                    "weekday": weekday,
                    "ranges": (
                        [
                            {"start": "10:00", "end": "13:00"},
                            {"start": "16:00", "end": "19:00"},
                        ]
                        if weekday == "monday"
                        else []
                    ),
                }
                for weekday in weekdays
            ],
        },
    )

    draft = build_booking_draft_from_input(
        project_input,
        
    )

    assert draft is not None

    configuration = finalize_booking_configuration(draft)

    assert configuration.services[0].id == "valoracion-inicial"
    assert configuration.services[0].duration_minutes == 45
    assert configuration.timezone == "Atlantic/Canary"
    assert configuration.slot_interval_minutes == 15
    assert len(configuration.weekly_schedule[0].ranges) == 2
    assert configuration.weekly_schedule[1].ranges == []


def test_rejects_duration_for_an_unknown_service():
    project_input = make_project_input(
        booking={
            "service_durations": {
                "servicio-inexistente": 45,
            },
        },
    )

    with pytest.raises(ValueError, match="Servicio desconocido"):
        build_booking_draft_from_input(
            project_input,
            
        )

def test_booking_uses_appointments_instead_of_business_catalog():
    project_input = make_project_input(
        services=[
            "Cambio de suspensión",
            "Reparación de averías",
        ],
        appointment_types=[
            "Recepción del vehículo",
        ],
        booking={
            "service_durations": {
                "recepcion-del-vehiculo": 20,
            },
        },
    )

    draft = build_booking_draft_from_input(
        project_input,
    )

    assert draft is not None
    assert len(draft.services) == 1
    assert draft.services[0].name == "Recepción del vehículo"
    assert draft.services[0].duration_minutes == 20


def test_catalog_does_not_automatically_become_bookable():
    project_input = make_project_input(
        services=["Reparación de averías"],
        appointment_types=[],
    )

    draft = build_booking_draft_from_input(
        project_input,
    )

    assert draft is None


def test_mixed_appointments_only_book_the_options_with_duration():
    project_input = make_project_input(
        appointment_types=[
            "Reparación de avería",
            "Recepción del vehículo",
            "Diagnóstico inicial",
        ],
        booking={
            "service_durations": {
                "recepcion-del-vehiculo": 20,
                "diagnostico-inicial": 45,
            },
            "appointment_modes": {"reparacion-de-averia": "pending_arrival"},
        },
    )

    draft = build_booking_draft_from_input(project_input)

    assert draft is not None
    assert [service.id for service in draft.services] == [
        "recepcion-del-vehiculo", "diagnostico-inicial",
    ]
    assert get_request_only_appointments(project_input) == []
    assert get_booking_missing_information(draft).service_durations == []
    assert [option.id for option in draft.pending_arrival_types] == [
        "reparacion-de-averia"
    ]


def test_pending_only_configuration_is_ready_with_schedule():
    project_input = make_project_input(
        services=["Reparación de avería"],
        appointment_types=["Entrega del vehículo"],
        booking={
            "timezone": "Europe/Madrid",
            "slot_interval_minutes": 30,
            "appointment_modes": {"entrega-del-vehiculo": "pending_arrival"},
            "weekly_schedule": [
                {"weekday": weekday, "ranges": (
                    [{"start": "09:00", "end": "14:00"}]
                    if weekday == "monday" else []
                )}
                for weekday in (
                    "monday", "tuesday", "wednesday", "thursday",
                    "friday", "saturday", "sunday",
                )
            ],
        },
    )

    draft = build_booking_draft_from_input(project_input)
    assert draft is not None
    assert get_booking_missing_information(draft).is_complete
    configuration = finalize_booking_configuration(draft)
    assert configuration.services == []
    assert configuration.pending_arrival_types[0].name == "Entrega del vehículo"


def test_inquiry_only_needs_timezone_but_not_hours():
    project_input = make_project_input(
        appointment_types=["Pedir presupuesto"],
        booking={"timezone": "Europe/Madrid"},
    )
    draft = build_booking_draft_from_input(project_input)
    assert draft is not None
    assert get_booking_missing_information(draft).is_complete
    configuration = finalize_booking_configuration(draft)
    assert configuration.inquiry_types[0].name == "Pedir presupuesto"
    assert configuration.weekly_schedule == []
