import re 
import unicodedata

def generate_service_id(
        service_name: str,
        existing_ids: set[str] | None = None,
) -> str:

    existing_ids = existing_ids or set()

    normalized_name = unicodedata.normalize(
        "NFKD",
        service_name,
    )

    without_accents = "".join(
        character
        for character in normalized_name
        if not unicodedata.combining(character)
    )

    base_id = re.sub(
        r"[^a-z0-9]+",
        "-",
        without_accents.lower(),
    ).strip("-")

    if not base_id:
        raise ValueError(
            "No se puede generar un service_id válido."
        )

    if base_id not in existing_ids:
        return base_id

    suffix = 2

    while f"{base_id}-{suffix}" in existing_ids:
        suffix += 1

    return f"{base_id}-{suffix}"