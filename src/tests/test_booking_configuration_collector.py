import pytest

from capabilities.booking.configuration_builder import (
    build_booking_configuration_draft,
)
from capabilities.booking.configuration_collector import (
    apply_booking_information,
)
from capabilities.models.booking import (
    BookingCollectedInformation,
    BookingDaySchedule,
    BookingTimeRange,
)


def test_apply_booking_information():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
            "Suspensión",
        ]
    )

    information = BookingCollectedInformation(
        service_durations={
            "frenos": 60,
            "suspension": 120,
        },
        timezone="Europe/Madrid",
        weekly_schedule=[
            BookingDaySchedule(
                weekday="monday",
                ranges=[
                    BookingTimeRange(
                        start="09:00",
                        end="14:00",
                    )
                ],
            )
        ],
        slot_interval_minutes=30,
    )

    updated = apply_booking_information(
        draft,
        information,
    )

    assert (
        updated.services[0].duration_minutes
        == 60
    )

    assert (
        updated.services[1].duration_minutes
        == 120
    )

    assert updated.timezone == "Europe/Madrid"

    assert (
        updated.slot_interval_minutes
        == 30
    )

    assert updated.weekly_schedule is not None


def test_apply_booking_information_does_not_mutate_original():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
        ]
    )

    information = BookingCollectedInformation(
        service_durations={
            "frenos": 60,
        }
    )

    updated = apply_booking_information(
        draft,
        information,
    )

    assert (
        draft.services[0].duration_minutes
        is None
    )

    assert (
        updated.services[0].duration_minutes
        == 60
    )


def test_apply_booking_information_rejects_unknown_service():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
        ]
    )

    information = BookingCollectedInformation(
        service_durations={
            "corte-de-pelo": 30,
        }
    )

    with pytest.raises(ValueError):
        apply_booking_information(
            draft,
            information,
        )