from typing import Literal
from pydantic import BaseModel

CapabilityType = Literal[
    "booking",
    "contact_form",
    "whatsapp",
    "maps",
    "gallery",
    "reviews",
    "analytics",
]

class CapabilitySpec(BaseModel):
    type: CapabilityType
    required: bool
    reason: str

class CapabilityPlan(BaseModel):
    capabilities: list[CapabilitySpec]
    