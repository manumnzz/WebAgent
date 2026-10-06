from pydantic import BaseModel

from agents.business_agent import BusinessProfile
from agents.ux_agent import WebsiteStructure
from agents.copy_agent import WebsiteCopy
from agents.design_agent import DesignSpec
from agents.developer_agent import DevelopmentResult
from validation.validator import ValidationResult
from specs.website_spec import WebsiteSpec
from specs.capability_spec import CapabilityPlan


class ProjectState(BaseModel):
    business: BusinessProfile | None = None
    ux: WebsiteStructure | None = None
    website_copy: WebsiteCopy | None = None
    design: DesignSpec | None = None
    website_spec: WebsiteSpec | None = None
    development: DevelopmentResult | None = None
    validation: ValidationResult | None = None
    capability_plan: CapabilityPlan | None = None


