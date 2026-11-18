from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)

from agents.business_agent import ContactInfo
from validation.checks.public_content import find_internal_notes


Weekday = Literal[
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
]


class OpeningHoursEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    weekday: Weekday
    hours: str = Field(min_length=1, max_length=120)


class GalleryImage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(pattern=r"^assets/[A-Za-z0-9_-]+\.(?:jpg|jpeg|png|webp)$")
    alt: str = Field(default="", max_length=300)


class ServiceContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, frozen=True)

    name: str = Field(
        min_length=1,
        max_length=120,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    price: str | None = Field(
        default=None,
        max_length=80,
    )


class WebsiteContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[2] = 2

    business_name: str = Field(
        min_length=1,
    )

    contact: ContactInfo = Field(
        default_factory=ContactInfo,
    )

    services: list[ServiceContent] = Field(
        default_factory=list,
    )

    opening_hours: list[OpeningHoursEntry] = Field(default_factory=list, max_length=7)
    gallery: list[GalleryImage] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_public_fields(self):
        service_ids = [
            service.id
            for service in self.services
        ]

        if len(service_ids) != len(set(service_ids)):
            raise ValueError(
                "Los servicios tienen identificadores duplicados."
            )

        if len({entry.weekday for entry in self.opening_hours}) != len(self.opening_hours):
            raise ValueError("Los horarios comerciales tienen días duplicados.")

        if len({image.path for image in self.gallery}) != len(self.gallery):
            raise ValueError("La galería tiene imágenes duplicadas.")

        texts = [
            self.business_name,
            *self.contact.model_dump().values(),
            *(text for service in self.services for text in (
                service.name, service.description, service.price,
            )),
            *(entry.hours for entry in self.opening_hours),
            *(image.alt for image in self.gallery),
        ]
        if any(find_internal_notes(text) for text in texts if text):
            raise ValueError("El contenido público incluye una nota interna.")

        return self
