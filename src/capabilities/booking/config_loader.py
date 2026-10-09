from pathlib import Path

from capabilities.models.booking import (
    BookingConfiguration,
)


def load_booking_configuration(
    path: str | Path,
) -> BookingConfiguration:

    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"No existe la configuración de Booking: "
            f"{config_path}"
        )

    return BookingConfiguration.model_validate_json(
        config_path.read_text(
            encoding="utf-8"
        )
    )