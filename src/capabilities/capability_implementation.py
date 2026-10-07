from pydantic import BaseModel

from specs.capability_spec import CapabilityType

class CapabilityImplementation(BaseModel):
    type: CapabilityType

    html: str
    css: str
    javascript: str

    implementation_notes: list[str]