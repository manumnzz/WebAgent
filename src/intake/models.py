from enum import StrEnum

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)

from capabilities.models.booking import BookingCollectedInformation
from content.models import OpeningHoursEntry


class RequestedFeature(StrEnum):
    WHATSAPP = "whatsapp"
    CONTACT_FORM = "contact_form"
    MAPS = "maps"
    GALLERY = "gallery"
    REVIEWS = "reviews"
    BOOKING = "booking"

class BusinessContactInput(BaseModel):
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    address: str | None = None


class ServiceDetailInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

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



class ProjectInput(BaseModel):
    business_name: str = Field(min_length=1)
    business_description: str = Field(min_length=1)

    business_type: str | None = None
    location: str | None = None

    services: list[str] = Field(default_factory=list)
    service_details: list[ServiceDetailInput] = Field(
        default_factory=list,
    )

    appointment_types: list[str] = Field(
        default_factory=list
    )

    contact: BusinessContactInput = Field(
        default_factory=BusinessContactInput
    )

    opening_hours: list[OpeningHoursEntry] = Field(default_factory=list, max_length=7)

    booking: BookingCollectedInformation | None = None

    main_goal: str | None = None

    desired_style: list[str] = Field(default_factory=list)
    reference_websites: list[str] = Field(default_factory=list)

    requested_features: list[RequestedFeature] = Field(
        default_factory=list
    )

    additional_notes: str | None = None

    @model_validator(mode="after")
    def validate_service_details(self):
        service_names = set(self.services)
        detailed_names = set()

        for detail in self.service_details:
            if detail.name not in service_names:
                raise ValueError(
                    f"El servicio '{detail.name}' "
                    "no existe en services."
                )

            if detail.name in detailed_names:
                raise ValueError(
                    f"Detalles duplicados para "
                    f"'{detail.name}'."
                )

            detailed_names.add(detail.name)

        if len({entry.weekday for entry in self.opening_hours}) != len(self.opening_hours):
            raise ValueError("Los horarios comerciales tienen días duplicados.")

        return self
