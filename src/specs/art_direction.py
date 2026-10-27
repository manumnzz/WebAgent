"""Concrete design decisions, persisted with the website contract."""

from pydantic import BaseModel, Field
from typing import Literal


class AssetDecision(BaseModel):
    path: str
    status: Literal["use", "avoid"]
    role: str
    reason: str


class ArtDirection(BaseModel):
    concept: str = ""
    audience_and_goal: str = ""
    signature_element: str = ""
    visual_hierarchy: str = ""
    composition_rhythm: str = ""
    image_strategy: str = ""
    alternatives_considered: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    asset_decisions: list[AssetDecision] = Field(default_factory=list)


class SectionComposition(BaseModel):
    desktop: str = ""
    mobile: str = ""
    focal_point: str = ""
    content_width: str = ""
    surface: str = ""
    asset_paths: list[str] = Field(default_factory=list)
    image_fit: str = ""
