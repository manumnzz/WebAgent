from datetime import date, time

import pytest

from capabilities.booking.booking_manager import (
    BookingManager,
    BookingSlotUnavailableError,
)
from capabilities.booking.fake_calendar_provider import (
    FakeCalendarProvider,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingDaySchedule,
    BookingRequest,
    BookingService,
    BookingTimeRange,
)


def build_configuration():

    return BookingConfiguration(
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


def test_booking_manager_returns_available_slots():

    manager = BookingManager(
        configuration=build_configuration(),
        calendar_provider=FakeCalendarProvider(),
    )

    slots = manager.get_available_slots(
        booking_date=date(
            2026,
            10,
            16,
        ),
        service_id="haircut",
    )

    assert len(slots) == 10

    assert slots[0].time() == time(
        9,
        0,
    )

    assert slots[-1].time() == time(
        13,
        30,
    )


def test_booking_manager_creates_booking():

    provider = FakeCalendarProvider()

    manager = BookingManager(
        configuration=build_configuration(),
        calendar_provider=provider,
    )

    request = BookingRequest(
        first_name="Manuel",
        last_name="Buzón",
        email="manuel@example.com",
        service_id="haircut",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            11,
            0,
        ),
    )

    confirmation = manager.create_booking(
        request
    )

    assert confirmation.event_id in (
        provider.created_events
    )

    assert confirmation.service_id == (
        "haircut"
    )

    assert confirmation.service_name == (
        "Corte"
    )

    assert confirmation.start.time() == (
        time(11, 0)
    )

    assert confirmation.end.time() == (
        time(11, 30)
    )


def test_booking_manager_prevents_double_booking():

    provider = FakeCalendarProvider()

    manager = BookingManager(
        configuration=build_configuration(),
        calendar_provider=provider,
    )

    first_request = BookingRequest(
        first_name="Manuel",
        last_name="Buzón",
        email="manuel@example.com",
        service_id="haircut",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            11,
            0,
        ),
    )

    manager.create_booking(
        first_request
    )

    second_request = BookingRequest(
        first_name="Carlos",
        last_name="Pérez",
        phone="600123123",
        service_id="haircut",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            11,
            0,
        ),
    )

    with pytest.raises(
        BookingSlotUnavailableError
    ):
        manager.create_booking(
            second_request
        )


def test_booking_manager_prevents_overlapping_service():

    provider = FakeCalendarProvider()

    manager = BookingManager(
        configuration=build_configuration(),
        calendar_provider=provider,
    )

    first_request = BookingRequest(
        first_name="Manuel",
        last_name="Buzón",
        email="manuel@example.com",
        service_id="haircut",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            10,
            0,
        ),
    )

    manager.create_booking(
        first_request
    )

    second_request = BookingRequest(
        first_name="Carlos",
        last_name="Pérez",
        phone="600123123",
        service_id="cut_beard",
        booking_date=date(
            2026,
            10,
            16,
        ),
        booking_time=time(
            9,
            30,
        ),
    )

    with pytest.raises(
        BookingSlotUnavailableError
    ):
        manager.create_booking(
            second_request
        )