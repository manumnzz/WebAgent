import json

import pytest
from pydantic import ValidationError

from capabilities.booking.config_loader import (
    load_booking_configuration,
)


def test_load_booking_configuration(
    tmp_path,
):

    config_path = (
        tmp_path
        / "booking.json"
    )

    config_path.write_text(
        json.dumps(
            {
                "timezone": "Europe/Madrid",
                "services": [
                    {
                        "id": "service-one",
                        "name": "Servicio uno",
                        "duration_minutes": 30,
                    }
                ],
                "weekly_schedule": [
                    {
                        "weekday": "monday",
                        "ranges": [
                            {
                                "start": "09:00:00",
                                "end": "14:00:00",
                            }
                        ],
                    }
                ],
                "slot_interval_minutes": 30,
            }
        ),
        encoding="utf-8",
    )

    configuration = (
        load_booking_configuration(
            config_path
        )
    )

    assert (
        configuration.timezone
        == "Europe/Madrid"
    )

    assert (
        configuration.services[0].id
        == "service-one"
    )

    assert (
        configuration.services[0]
        .duration_minutes
        == 30
    )


def test_missing_booking_configuration():

    with pytest.raises(
        FileNotFoundError
    ):
        load_booking_configuration(
            "does-not-exist.json"
        )


def test_invalid_booking_configuration(
    tmp_path,
):

    config_path = (
        tmp_path
        / "booking.json"
    )

    config_path.write_text(
        json.dumps(
            {
                "timezone": "Europe/Madrid",
                "services": [
                    {
                        "id": "invalid",
                        "name": "Servicio",
                        "duration_minutes": 0,
                    }
                ],
                "weekly_schedule": [],
                "slot_interval_minutes": 30,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValidationError
    ):
        load_booking_configuration(
            config_path
        )