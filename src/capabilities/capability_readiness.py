from pydantic import BaseModel

from capabilities.capability_inputs import CapabilityInputs
from capabilities.capability_registry import CapabilityDefinition
from specs.capability_spec import CapabilityType

class CapabilityReadiness(BaseModel):
    type: CapabilityType
    ready: bool
    missing_inputs: list[str]

def evaluate_capability_readiness(definition: CapabilityDefinition, 
                                  inputs: CapabilityInputs) -> CapabilityReadiness:

    available_inputs = inputs.model_dump()

    missing_inputs = [
        required_input
        for required_input in definition.required_inputs
        if not available_inputs.get(required_input)
    ]

    return CapabilityReadiness(
        type=definition.type,
        ready=not missing_inputs,
        missing_inputs=missing_inputs,
    )