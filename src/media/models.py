from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


MediaRole = Literal["logo", "gallery"]
ImageFormat = Literal["jpg", "png", "webp"]


class MediaAsset(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    role: MediaRole
    format: ImageFormat

    width: int = Field(gt=0)
    height: int = Field(gt=0)
    size_bytes: int = Field(gt=0)

    source: Literal["customer_upload"] = "customer_upload"

    alt_text: str | None = Field(
        default=None,
        max_length=300,
    )

    @property
    def filename(self) -> str:
        return f"{self.id.hex}.{self.format}"

    @property
    def public_path(self) -> str:
        return f"assets/{self.filename}"


class MediaManifest(BaseModel):
    assets: list[MediaAsset] = Field(
        default_factory=list,
    )

    @model_validator(mode="after")
    def validate_assets(self):
        asset_ids = [asset.id for asset in self.assets]

        if len(asset_ids) != len(set(asset_ids)):
            raise ValueError(
                "Los recursos multimedia tienen identificadores repetidos."
            )

        logo_count = sum(
            asset.role == "logo"
            for asset in self.assets
        )

        if logo_count > 1:
            raise ValueError(
                "El encargo solo puede tener un logo."
            )

        return self

class WebsiteMediaAsset(MediaAsset):
    path: str

    