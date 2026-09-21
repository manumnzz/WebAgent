from pydantic import BaseModel

from agents.business_agent import BusinessProfile
from agents.ux_agent import WebsiteStructure
from agents.copy_agent import WebsiteCopy
from agents.design_agent import DesignSpec
from specs.website_spec import WebsiteSpec

class ProjectState(BaseModel):
    business: BusinessProfile | None = None
    ux: WebsiteStructure | None = None
    website_copy: WebsiteCopy | None = None
    design: DesignSpec | None = None
    website_spec: WebsiteSpec | None = None


