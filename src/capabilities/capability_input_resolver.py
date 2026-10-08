from agents.business_agent import BusinessProfile
from capabilities.capability_inputs import CapabilityInputs

def resolve_business_capability_inputs(
        business: BusinessProfile,
        current_inputs: CapabilityInputs | None = None,
) -> CapabilityInputs:

    inputs = (
        current_inputs.model_copy(deep=True)
        if current_inputs is not None
        else CapabilityInputs()
    )

    if business.contact.whatsapp:
        inputs.whatsapp_number = (
            business.contact.whatsapp
        )

    if business.contact.email:
        inputs.contact_destination = (
            business.contact.email
        )

    if business.contact.address:
        inputs.business_address = (
            business.contact.address
        )

    return inputs

