from pydantic import BaseModel

class CapabilityInputs(BaseModel):
    booking_configuration: dict | None = None
    contact_destination: str | None = None
    whatsapp_number: str | None = None
    business_address: str | None = None
    gallery_assets: list[str] | None = None
    review_data: list[dict] | None = None
    analytics_configuration: dict | None = None