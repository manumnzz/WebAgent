from datetime import date, time

import pytest
from pydantic import ValidationError

from capabilities.models.booking import (
    BookingConfiguration,
    BookingDaySchedule,
    BookingRequest,
    BookingService,
    BookingTimeRange,
)

from capabilities.capability_inputs import CapabilityInputs

from capabilities.capability_readiness import (
    evaluate_capability_readiness,
)
from capabilities.capability_registry import (
    get_capability_definition,
)


def test_booking_service():

    service = BookingService(
        id="cut_beard",
        name="Corte + barba",
        duration_minutes=45,
    )

    assert service.id == "cut_beard"
    assert service.name == "Corte + barba"
    assert service.duration_minutes == 45


def test_booking_service_rejects_invalid_duration():

    with pytest.raises(ValidationError):

        BookingService(
            id="haircut",
            name="Corte",
            duration_minutes=0,
        )


def test_booking_time_range():

    time_range = BookingTimeRange(
        start=time(9, 0),
        end=time(14, 0),
    )

    assert time_range.start == time(9, 0)
    assert time_range.end == time(14, 0)


def test_booking_time_range_rejects_invalid_range():

    with pytest.raises(ValidationError):

        BookingTimeRange(
            start=time(18, 0),
            end=time(9, 0),
        )


def test_booking_configuration():

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
                weekday="monday",
                ranges=[
                    BookingTimeRange(
                        start=time(9, 0),
                        end=time(14, 0),
                    ),
                    BookingTimeRange(
                        start=time(16, 0),
                        end=time(20, 0),
                    ),
                ],
            )
        ],
        slot_interval_minutes=30,
    )

    assert configuration.timezone == "Europe/Madrid"
    assert len(configuration.services) == 2
    assert len(configuration.weekly_schedule) == 1

    assert (
        configuration.weekly_schedule[0]
        .ranges[1]
        .start
        == time(16, 0)
    )


def test_booking_request():

    request = BookingRequest(
        first_name="Manuel",
        last_name="Buzón",
        email="manuel@example.com",
        service_id="cut_beard",
        booking_date=date(2026, 10, 16),
        booking_time=time(11, 30),
        notes="Prefiero degradado bajo.",
    )

    assert request.first_name == "Manuel"
    assert request.service_id == "cut_beard"
    assert request.booking_time == time(11, 30)


def test_booking_request_accepts_phone_without_email():

    request = BookingRequest(
        first_name="Carlos",
        last_name="Pérez",
        phone="600123123",
        service_id="haircut",
        booking_date=date(2026, 10, 16),
        booking_time=time(10, 0),
    )

    assert request.phone == "600123123"
    assert request.email is None


def test_booking_request_requires_contact():

    with pytest.raises(ValidationError):

        BookingRequest(
            first_name="Carlos",
            last_name="Pérez",
            service_id="haircut",
            booking_date=date(2026, 10, 16),
            booking_time=time(10, 0),
        )

def test_booking_configuration_can_be_used_as_capability_input():

    configuration = BookingConfiguration(
        timezone="Europe/Madrid",
        services=[
            BookingService(
                id="haircut",
                name="Corte",
                duration_minutes=30,
            )
        ],
        weekly_schedule=[
            BookingDaySchedule(
                weekday="monday",
                ranges=[
                    BookingTimeRange(
                        start=time(9, 0),
                        end=time(14, 0),
                    )
                ],
            )
        ],
    )

    inputs = CapabilityInputs(
        booking_configuration=configuration
    )

    assert inputs.booking_configuration is not None
    assert (
        inputs.booking_configuration.services[0].id
        == "haircut"
    )

def test_booking_capability_is_ready_with_configuration():

    configuration = BookingConfiguration(
        timezone="Europe/Madrid",
        services=[
            BookingService(
                id="haircut",
                name="Corte",
                duration_minutes=30,
            )
        ],
        weekly_schedule=[
            BookingDaySchedule(
                weekday="monday",
                ranges=[
                    BookingTimeRange(
                        start=time(9, 0),
                        end=time(14, 0),
                    )
                ],
            )
        ],
    )

    inputs = CapabilityInputs(
        booking_configuration=configuration
    )

    definition = get_capability_definition(
        "booking"
    )

    readiness = evaluate_capability_readiness(
        definition,
        inputs,
    )

    assert readiness.ready is True
    assert readiness.missing_inputs == []

def test_booking_capability_is_not_ready_without_configuration():

    inputs = CapabilityInputs()

    definition = get_capability_definition(
        "booking"
    )

    readiness = evaluate_capability_readiness(
        definition,
        inputs,
    )

    assert readiness.ready is False
    assert readiness.missing_inputs == [
        "booking_configuration"
    ]