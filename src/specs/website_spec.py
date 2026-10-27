from pydantic import BaseModel, Field
from typing import Any

from agents.business_agent import BusinessProfile
from specs.capability_spec import CapabilityType
from media.models import WebsiteMediaAsset

from capabilities.placement_policy import (
    CapabilityPlacementPolicy,
)

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

class WebsiteCapabilitySpec(BaseModel):
    type: CapabilityType
    required: bool
    reason: str

    description: str

    required_inputs: list[str]
    ready: bool
    missing_inputs: list[str]
    input_values: dict[str, Any]

    developer_requirements: list[str]

    placement_policy: CapabilityPlacementPolicy = Field(
        default_factory=CapabilityPlacementPolicy,
    )

class WebsiteSpec(BaseModel):
    business: BusinessProfile

    available_media: list[WebsiteMediaAsset] = Field(
        default_factory=list,
    )

    navigation: list[str]
    primary_cta: str | None

    visual_direction: str
    color_palette: list[str]
    typography_direction: str

    sections: list[WebsiteSectionSpec]

    capabilities: list[WebsiteCapabilitySpec]

    missing_content: list[str]
    missing_information: list[str]
    missing_assets: list[str]

