from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from pydantic import BaseModel, ConfigDict

from specs.website_spec import WebsiteSpec


class WebsiteSpecSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    website_spec: WebsiteSpec


def save_website_spec(
    specification: WebsiteSpec,
    path: str | Path,
) -> None:
    destination = Path(path)

    snapshot = WebsiteSpecSnapshot(
        schema_version=1,
        website_spec=specification,
    )

    content = snapshot.model_dump_json(indent=2)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with TemporaryDirectory(
        dir=destination.parent,
        prefix="website-spec-",
    ) as temporary_directory:
        temporary_path = (
            Path(temporary_directory) / "website_spec.json"
        )

        temporary_path.write_text(
            content,
            encoding="utf-8",
        )

        temporary_path.replace(destination)


def load_website_spec(
    path: str | Path,
) -> WebsiteSpec:
    source = Path(path)

    if not source.is_file():
        raise FileNotFoundError(
            f"No existe el contrato de la web: {source}"
        )

    snapshot = WebsiteSpecSnapshot.model_validate_json(
        source.read_text(encoding="utf-8"),
    )

    return snapshot.website_spec