from pydantic import BaseModel

from agents.business_agent import BusinessProfile

class WebsiteSectionSpec(BaseModel):
    name: str
    purpose: str

    headline: str | None
    body: str | None
    cta: str | None

    copy_ready: bool
    missing_copy_requirements: list[str]

    layout: str
    visual_notes: str
    required_inputs: list[str]

class WebsiteSpec(BaseModel):
    business: BusinessProfile

    navigation: list[str]
    primary_cta: str | None

    visual_direction: str
    color_palette: list[str]
    typography_direction: str

    sections: list[WebsiteSectionSpec]

    missing_content: list[str]
    missing_information: list[str]
    missing_assets: list[str]

