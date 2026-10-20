from capabilities.booking.configuration_builder import (
    build_booking_service_drafts,
)


def test_build_booking_service_drafts():

    services = build_booking_service_drafts(
        [
            "Cambio de aceite y filtros",
            "Frenos",
            "Neumáticos",
            "Suspensión",
            "Diagnosis electrónica",
        ]
    )

    assert len(services) == 5

    assert services[0].id == (
        "cambio-de-aceite-y-filtros"
    )

    assert services[0].name == (
        "Cambio de aceite y filtros"
    )

    assert services[0].duration_minutes is None

    assert services[4].id == (
        "diagnosis-electronica"
    )


def test_booking_service_drafts_ignore_duplicates():

    services = build_booking_service_drafts(
        [
            "Frenos",
            "Frenos",
            "frenos",
        ]
    )

    assert len(services) == 1
    assert services[0].id == "frenos"


def test_booking_service_drafts_ignore_empty_names():

    services = build_booking_service_drafts(
        [
            "Frenos",
            "",
            "   ",
        ]
    )

    assert len(services) == 1

from capabilities.booking.configuration_builder import (
    build_booking_configuration_draft,
    build_booking_service_drafts,
)


def test_build_booking_configuration_draft():

    draft = build_booking_configuration_draft(
        [
            "Cambio de aceite y filtros",
            "Frenos",
            "Neumáticos",
            "Suspensión",
            "Escapes",
            "Diagnosis electrónica",
        ]
    )

    assert len(draft.services) == 6

    assert (
        draft.services[0].id
        == "cambio-de-aceite-y-filtros"
    )

    assert (
        draft.services[5].id
        == "diagnosis-electronica"
    )

    assert draft.timezone is None
    assert draft.weekly_schedule is None
    assert draft.slot_interval_minutes is None

    assert all(
        service.duration_minutes is None
        for service in draft.services
    )