from pathlib import Path

from capabilities.models.booking import (
    BookingConfiguration,
)


def save_booking_configuration(
    configuration: BookingConfiguration,
    path: str | Path = "config/booking.json",
) -> None:

    config_path = Path(path)

    config_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    config_path.write_text(
        configuration.model_dump_json(
            indent=2,
        ),
        encoding="utf-8",
    )