import pytest

from capabilities.booking.service_id import (
    generate_service_id,
)


def test_generate_simple_service_id():
    service_id = generate_service_id(
        "Corte"
    )

    assert service_id == "corte"


def test_generate_service_id_normalizes_accents():
    service_id = generate_service_id(
        "Sesión de fisioterapia"
    )

    assert service_id == "sesion-de-fisioterapia"


def test_generate_service_id_normalizes_separators():
    service_id = generate_service_id(
        "Corte + barba"
    )

    assert service_id == "corte-barba"


def test_generate_service_id_avoids_collision():
    service_id = generate_service_id(
        "Corte",
        existing_ids={
            "corte",
        },
    )

    assert service_id == "corte-2"


def test_generate_service_id_uses_next_available_suffix():
    service_id = generate_service_id(
        "Corte",
        existing_ids={
            "corte",
            "corte-2",
            "corte-3",
        },
    )

    assert service_id == "corte-4"


def test_generate_service_id_rejects_invalid_name():
    with pytest.raises(ValueError):
        generate_service_id(
            "!!!"
        )