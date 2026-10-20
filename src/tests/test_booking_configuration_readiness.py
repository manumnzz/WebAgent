from capabilities.booking.configuration_builder import (
    build_booking_configuration_draft,
)
from capabilities.booking.configuration_readiness import (
    get_booking_missing_information,
)


def test_detects_missing_booking_information():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
            "Suspensión",
        ]
    )

    missing = get_booking_missing_information(
        draft
    )

    assert missing.service_durations == [
        "frenos",
        "suspension",
    ]

    assert missing.timezone is True
    assert missing.weekly_schedule is True
    assert missing.slot_interval_minutes is True

    assert missing.is_complete is False


def test_detects_only_information_that_is_missing():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
            "Suspensión",
        ]
    )

    draft.timezone = "Europe/Madrid"
    draft.slot_interval_minutes = 30

    draft.services[0].duration_minutes = 60

    missing = get_booking_missing_information(
        draft
    )

    assert missing.service_durations == [
        "suspension",
    ]

    assert missing.timezone is False
    assert missing.weekly_schedule is True
    assert missing.slot_interval_minutes is False

    assert missing.is_complete is False

def test_booking_draft_can_be_complete():

    draft = build_booking_configuration_draft(
        [
            "Frenos",
        ]
    )

    draft.timezone = "Europe/Madrid"
    draft.slot_interval_minutes = 30

    draft.services[0].duration_minutes = 60

    draft.weekly_schedule = []

    missing = get_booking_missing_information(
        draft
    )

    assert missing.service_durations == []
    assert missing.timezone is False
    assert missing.weekly_schedule is False
    assert missing.slot_interval_minutes is False

    assert missing.is_complete is True