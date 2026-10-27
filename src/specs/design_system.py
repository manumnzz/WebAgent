from typing import Annotated, Literal

from pydantic import BaseModel, Field


HexColor = Annotated[
    str,
    Field(pattern=r"^#[0-9a-fA-F]{6}$"),
]


class ColorTokens(BaseModel):
    background: HexColor = "#FFFFFF"
    surface: HexColor = "#F4F4F5"
    text: HexColor = "#18181B"
    muted_text: HexColor = "#52525B"
    accent: HexColor = "#2563EB"
    accent_text: HexColor = "#FFFFFF"
    border: HexColor = "#D4D4D8"


class TypographyTokens(BaseModel):
    heading_family: str = Field(
        default="system-ui",
        min_length=1,
    )

    body_family: str = Field(
        default="system-ui",
        min_length=1,
    )

    body_size_px: int = Field(
        default=16,
        ge=14,
        le=24,
    )


    heading_size_mobile_px: int = Field(default=40, ge=28, le=80)
    heading_size_desktop_px: int = Field(default=72, ge=40, le=140)
    section_heading_size_px: int = Field(default=40, ge=24, le=72)
    heading_line_height: float = Field(default=1.08, ge=0.95, le=1.4)
    body_line_height: float = Field(default=1.6, ge=1.4, le=1.9)
    body_max_width_ch: int = Field(default=62, ge=40, le=80)


class LayoutTokens(BaseModel):
    content_max_width_px: int = Field(
        default=1200,
        gt=0,
    )

    gutter_mobile_px: int = Field(
        default=20,
        gt=0,
    )

    gutter_desktop_px: int = Field(
        default=40,
        gt=0,
    )

    section_spacing_mobile_px: int = Field(
        default=64,
        gt=0,
    )

    section_spacing_desktop_px: int = Field(
        default=112,
        gt=0,
    )


class MotionTokens(BaseModel):
    hero_effect: Literal[
        "none",
        "fade",
        "fade-up",
    ] = "fade-up"

    scroll_effect: Literal[
        "none",
        "fade",
        "fade-up",
    ] = "fade"

    duration_ms: int = Field(
        default=480,
        ge=100,
        le=1200,
    )

    distance_px: int = Field(
        default=20,
        ge=0,
        le=64,
    )

    stagger_ms: int = Field(
        default=60,
        ge=0,
        le=200,
    )

    respect_reduced_motion: Literal[True] = True


class DesignSystem(BaseModel):
    colors: ColorTokens = Field(
        default_factory=ColorTokens,
    )

    typography: TypographyTokens = Field(
        default_factory=TypographyTokens,
    )

    layout: LayoutTokens = Field(
        default_factory=LayoutTokens,
    )

    motion: MotionTokens = Field(
        default_factory=MotionTokens,
    )