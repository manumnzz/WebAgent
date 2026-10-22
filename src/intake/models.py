from enum import StrEnum

from pydantic import BaseModel, Field

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

class ProjectInput(BaseModel):
    business_name: str = Field(min_length=1)
    business_description: str = Field(min_length=1)

    business_type: str | None = None
    location: str | None = None

    services: list[str] = Field(default_factory=list)

    contact: BusinessContactInput = Field(
        default_factory=BusinessContactInput
    )

    main_goal: str | None = None

    desired_style: list[str] = Field(default_factory=list)
    reference_websites: list[str] = Field(default_factory=list)

    requested_features: list[RequestedFeature] = Field(
        default_factory=list
    )

    additional_notes: str | None = None

    