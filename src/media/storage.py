from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from media.image_processing import (
    InvalidMediaError,
    prepare_image,
)
from media.models import (
    MediaManifest,
    MediaRole,
)


MAX_GALLERY_IMAGES = 20
MAX_BATCH_BYTES = 40 * 1024 * 1024


class MediaAlreadyExistsError(ValueError):
    pass

@dataclass(frozen=True)
class MediaUpload:
    content: bytes
    role: MediaRole
    alt_text: str | None = None


def load_media_manifest(
        submission_directory: str | Path,
) -> MediaManifest:
    media_directory = Path(submission_directory) / "media"

    if not media_directory.exists():
        return MediaManifest()

    manifest_path = media_directory / "media.json"

    return MediaManifest.model_validate_json(
        manifest_path.read_text(encoding="utf-8")
    )

def save_media_batch(
        submission_directory: str | Path,
        uploads: list[MediaUpload],
) -> MediaManifest:
    submission_directory = Path(
        submission_directory
    ).resolve()

    input_path = submission_directory / "project_input.json"

    if not input_path.is_file():
        raise FileNotFoundError(
            "No existe el encargo donde guardar las imágenes."
        )

    media_directory = submission_directory / "media"

    if media_directory.exists():
        raise MediaAlreadyExistsError(
            "Este campo ya tiene una entrega de multimeda."
        )

    if not uploads:
        raise InvalidMediaError(
            "Debes proporcionar al menos una imagen."
        )

    if len(uploads) > MAX_GALLERY_IMAGES + 1:
        raise InvalidMediaError(
            "Se admite un logo y hasta 20 fotos."
        )

    gallery_count = sum(
        upload.role == "gallery"
        for upload in uploads
    )

    if gallery_count > MAX_GALLERY_IMAGES:
        raise InvalidMediaError(
            "Se admiten como máximo 20 fotos de galería."
        )

    total_bytes = sum(
        len(upload.content)
        for upload in uploads
    )

    if total_bytes > MAX_BATCH_BYTES:
        raise InvalidMediaError(
            "El conjunto de imágenes supera los 40 MiB."
        )

    with TemporaryDirectory(
        prefix=".media-",
        dir=submission_directory,
    ) as temporary_directory:
        staged_directory = (
            Path(temporary_directory) / "prepared"
        )
        staged_directory.mkdir()

        assets = []

        for upload in uploads:
            asset, prepared_content = prepare_image(
                upload.content,
                role=upload.role,
                alt_text=upload.alt_text,
            )

            image_path = staged_directory / asset.filename
            image_path.write_bytes(prepared_content)

            assets.append(asset)

        manifest = MediaManifest(assets=assets)

        manifest_path = staged_directory / "media.json"
        manifest_path.write_text(
            manifest.model_dump_json(indent=2),
            encoding="utf-8",
        )

        staged_directory.rename(media_directory)

    return manifest