import re
import unicodedata

from specs.website_spec import WebsiteSpec

from content.models import (
    GalleryImage,
    WebsiteContent,
    ServiceContent,
)

from intake.models import ProjectInput


def normalize_identifier(value: str) -> str:
    """
    Normaliza un texto para utilizarlo como ID.
    """
    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    identifier = re.sub(
        r"[^a-z0-9]+",
        "-",
        without_accents.lower(),
    )

    return identifier.strip("-")


def generate_unique_id(
    value: str,
    used_ids: set[str],
    *,
    fallback: str | None = None,
) -> str:
    """
    Genera un identificador único.
    """
    base_id = normalize_identifier(value) or fallback

    if not base_id:
        raise ValueError("No se puede generar un identificador vacío.")

    candidate = base_id
    suffix = 2

    while candidate in used_ids:
        candidate = f"{base_id}-{suffix}"
        suffix += 1

    used_ids.add(candidate)

    return candidate



def build_service_content(
    website_spec: WebsiteSpec,
    project_input: ProjectInput | None = None,
) -> list[ServiceContent]:
    """
    Construye servicios con datos explícitos
    del encargo cuando están disponibles.
    """
    services = []
    used_ids = set()

    details_by_name = {}

    if project_input is not None:
        details_by_name = {
            detail.name: detail
            for detail in project_input.service_details
        }

    for service_name in website_spec.business.services:
        service_id = generate_unique_id(
            service_name,
            used_ids,
            fallback="servicio",
        )

        detail = details_by_name.get(service_name)

        services.append(
            ServiceContent(
                id=service_id,
                name=service_name,
                description=(
                    detail.description
                    if detail is not None
                    else None
                ),
                price=(
                    detail.price
                    if detail is not None
                    else None
                ),
            )
        )

    return services



def build_website_content(
    website_spec: WebsiteSpec,
    project_input: ProjectInput | None = None,
) -> WebsiteContent:
    """
    Construye el contenido operativo editable.

    No extrae copy editorial ni información
    interna de WebsiteSpec.
    """
    business = website_spec.business

    if not business.name or not business.name.strip():
        raise ValueError(
            "No se puede construir WebsiteContent "
            "sin el nombre del negocio."
        )

    return WebsiteContent(
        opening_hours=(
            [entry.model_copy(deep=True) for entry in project_input.opening_hours]
            if project_input is not None else []
        ),
        gallery=[
            GalleryImage(path=asset.path, alt=asset.alt_text or "")
            for asset in website_spec.available_media
            if asset.role == "gallery"
        ],
        business_name=business.name,
        contact=business.contact.model_copy(
            deep=True,
        ),
        services=build_service_content(
            website_spec,
            project_input,
        ),
    )
