from capabilities.booking.config_loader import (
    load_booking_configuration,
)
from capabilities.booking.config_writer import (
    save_booking_configuration,
)
from capabilities.models.booking import (
    BookingConfiguration,
)


def test_save_and_load_booking_configuration(
    tmp_path,
):

    configuration = (
        BookingConfiguration.model_validate(
            {
                "timezone": "Europe/Madrid",
                "services": [
                    {
                        "id": "frenos",
                        "name": "Frenos",
                        "duration_minutes": 60,
                    },
                    {
                        "id": "suspension",
                        "name": "Suspensión",
                        "duration_minutes": 120,
                    },
                ],
                "weekly_schedule": [
                    {
                        "weekday": "monday",
                        "ranges": [
                            {
                                "start": "09:00",
                                "end": "14:00",
                            }
                        ],
                    }
                ],
                "slot_interval_minutes": 30,
            }
        )
    )

    config_path = (
        tmp_path / "booking.json"
    )

    save_booking_configuration(
        configuration,
        config_path,
    )

    loaded = load_booking_configuration(
        config_path
    )

    assert config_path.exists()
    assert loaded == configuration

    assert loaded.services[0].id == "frenos"
    assert loaded.services[1].id == "suspension"