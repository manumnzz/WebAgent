import pytest

from capabilities.booking.configuration_builder import (
    build_booking_configuration_draft,
)
from capabilities.booking.configuration_collector import (
    apply_booking_information,
)
from capabilities.booking.configuration_finalizer import (
    finalize_booking_configuration,
)
from capabilities.models.booking import (
    BookingCollectedInformation,
    BookingDaySchedule,
    BookingTimeRange,
)


def test_finalize_booking_configuration():

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

    completed_draft = apply_booking_information(
        draft,
        information,
    )

    configuration = (
        finalize_booking_configuration(
            completed_draft
        )
    )

    assert (
        configuration.timezone
        == "Europe/Madrid"
    )

    assert len(configuration.services) == 2

    assert (
        configuration.services[0].id
        == "frenos"
    )

    assert (
        configuration.services[0].duration_minutes
        == 60
    )

    assert (
        configuration.services[1].id
        == "suspension"
    )

    assert (
        configuration.services[1].duration_minutes
        == 120
    )

    assert (
        configuration.slot_interval_minutes
        == 30
    )


def test_cannot_finalize_incomplete_booking():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
        ]
    )

    with pytest.raises(ValueError):
        finalize_booking_configuration(
            draft
        )