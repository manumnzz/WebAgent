from typing import Literal

from pydantic import BaseModel, Field


PlacementZone = Literal[
    "hero",
    "content",
    "contact",
    "floating",
    "navigation",
    "footer",
]


class CapabilityPlacementPolicy(BaseModel):
    max_instances: int = Field(default=1, ge=1)

    allowed_zones: tuple[PlacementZone, ...] | None = Field(
        default=None,
        min_length=1,
    )