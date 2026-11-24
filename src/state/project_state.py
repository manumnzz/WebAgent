from pydantic import BaseModel, Field

from agents.business_agent import BusinessProfile
from agents.ux_agent import WebsiteStructure
from agents.copy_agent import WebsiteCopy
from agents.design_agent import DesignSpec
from agents.developer_agent import DevelopmentResult
from validation.validator import ValidationResult
from specs.website_spec import WebsiteSpec
from specs.capability_spec import CapabilityPlan
from capabilities.capability_inputs import CapabilityInputs
from capabilities.models.booking import (
    BookingConfigurationDraft,
)
from intake.models import ProjectInput
from media.models import WebsiteMediaAsset

class ProjectState(BaseModel):
    project_input: ProjectInput | None = None
    available_media: list[WebsiteMediaAsset] = Field(
        default_factory=list,
    )
    
    business: BusinessProfile | None = None
    ux: WebsiteStructure | None = None
    capability_plan: CapabilityPlan | None = None
    capability_inputs: CapabilityInputs = Field(
        default_factory=CapabilityInputs
    )
    booking_configuration_draft: (
        BookingConfigurationDraft | None 
    ) = None
    website_copy: WebsiteCopy | None = None
    design: DesignSpec | None = None
    website_spec: WebsiteSpec | None = None
    development: DevelopmentResult | None = None
    validation: ValidationResult | None = None
    



