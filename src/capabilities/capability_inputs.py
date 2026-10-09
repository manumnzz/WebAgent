from pydantic import BaseModel

from capabilities.models.booking import BookingConfiguration
from capabilities.models.review import ReviewData

class CapabilityInputs(BaseModel):
    booking_configuration: BookingConfiguration | None = None
    contact_destination: str | None = None
    whatsapp_number: str | None = None
    business_address: str | None = None
    gallery_assets: list[str] | None = None
    review_data: list[ReviewData] | None = None
    analytics_configuration: dict | None = None