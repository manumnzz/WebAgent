from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from capabilities.booking.availability import (
    calculate_available_slots,
)
from capabilities.models.booking import (
    BookingConfiguration,
    BookingDaySchedule,
    BookingService,
    BookingTimeRange,
    CalendarBusyInterval,
)


TIMEZONE = ZoneInfo("Europe/Madrid")


def build_booking_configuration():
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


def test_calculate_available_slots():

    configuration = (
        build_booking_configuration()
    )

    busy_intervals = [
        CalendarBusyInterval(
            start=datetime(
                2026,
                10,
                16,
                10,
                0,
                tzinfo=TIMEZONE,
            ),
            end=datetime(
                2026,
                10,
                16,
                10,
                30,
                tzinfo=TIMEZONE,
            ),
        ),
        CalendarBusyInterval(
            start=datetime(
                2026,
                10,
                16,
                12,
                0,
                tzinfo=TIMEZONE,
            ),
            end=datetime(
                2026,
                10,
                16,
                13,
                0,
                tzinfo=TIMEZONE,
            ),
        ),
    ]

    slots = calculate_available_slots(
        configuration=configuration,
        booking_date=date(
            2026,
            10,
            16,
        ),
        service_id="haircut",
        busy_intervals=busy_intervals,
    )

    assert [
        slot.time()
        for slot in slots
    ] == [
        time(9, 0),
        time(9, 30),
        time(10, 30),
        time(11, 0),
        time(11, 30),
        time(13, 0),
        time(13, 30),
    ]


def test_service_duration_affects_availability():

    configuration = (
        build_booking_configuration()
    )

    busy_intervals = [
        CalendarBusyInterval(
            start=datetime(
                2026,
                10,
                16,
                10,
                0,
                tzinfo=TIMEZONE,
            ),
            end=datetime(
                2026,
                10,
                16,
                10,
                30,
                tzinfo=TIMEZONE,
            ),
        )
    ]

    slots = calculate_available_slots(
        configuration=configuration,
        booking_date=date(
            2026,
            10,
            16,
        ),
        service_id="cut_beard",
        busy_intervals=busy_intervals,
    )

    slot_times = [
        slot.time()
        for slot in slots
    ]

    assert time(9, 0) in slot_times

    assert time(9, 30) not in slot_times

    assert time(10, 0) not in slot_times

    assert time(10, 30) in slot_times


def test_returns_empty_when_business_is_closed():

    configuration = (
        build_booking_configuration()
    )

    slots = calculate_available_slots(
        configuration=configuration,
        booking_date=date(
            2026,
            10,
            18,
        ),
        service_id="haircut",
        busy_intervals=[],
    )

    assert slots == []


def test_unknown_service_is_rejected():

    configuration = (
        build_booking_configuration()
    )

    with pytest.raises(ValueError):

        calculate_available_slots(
            configuration=configuration,
            booking_date=date(
                2026,
                10,
                16,
            ),
            service_id="does_not_exist",
            busy_intervals=[],
        )


def test_busy_interval_boundaries_do_not_overlap():

    configuration = (
        build_booking_configuration()
    )

    busy_intervals = [
        CalendarBusyInterval(
            start=datetime(
                2026,
                10,
                16,
                10,
                0,
                tzinfo=TIMEZONE,
            ),
            end=datetime(
                2026,
                10,
                16,
                10,
                30,
                tzinfo=TIMEZONE,
            ),
        )
    ]

    slots = calculate_available_slots(
        configuration=configuration,
        booking_date=date(
            2026,
            10,
            16,
        ),
        service_id="haircut",
        busy_intervals=busy_intervals,
    )

    slot_times = [
        slot.time()
        for slot in slots
    ]

    assert time(9, 30) in slot_times
    assert time(10, 0) not in slot_times
    assert time(10, 30) in slot_times