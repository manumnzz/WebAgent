from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from media.image_processing import (
    MAX_UPLOAD_BYTES,
    InvalidMediaError,
)
from media.models import MediaManifest
from media.storage import (
    MAX_BATCH_BYTES,
    MAX_GALLERY_IMAGES,
    MediaAlreadyExistsError,
    MediaUpload,
    save_media_batch,
)



def create_media_router(
    storage_directory: Path,
) -> APIRouter:
    router = APIRouter(
        prefix="/intake",
        tags=["media"],
    )

    @router.post(
        "/{submission_id}/media",
        response_model=MediaManifest,
        status_code=201,
    )
    def receive_media(
        submission_id: UUID,
        logo: Annotated[UploadFile | None, File()] = None,
        gallery: Annotated[
            list[UploadFile] | None,
            File(),
        ] = None,
    ) -> MediaManifest:
        submission_directory = (
            storage_directory / submission_id.hex
        )

        if not (
            submission_directory / "project_input.json"
        ).is_file():
            raise HTTPException(
                status_code=404,
                detail="No existe el encargo indicado.",
            )

        if (submission_directory / "media").exists():
            raise HTTPException(
                status_code=409,
                detail=(
                    "Este encargo ya tiene una entrega "
                    "de multimedia."
                ),
            )

        gallery_files = gallery or []

        if len(gallery_files) > MAX_GALLERY_IMAGES:
            raise HTTPException(
                status_code=422,
                detail="Se admiten como máximo 20 fotos.",
            )

        files_to_read = []

        if logo is not None:
            files_to_read.append((logo, "logo"))

        files_to_read.extend(
            (file, "gallery")
            for file in gallery_files
        )

        if not files_to_read:
            raise HTTPException(
                status_code=422,
                detail="Debes proporcionar al menos una imagen.",
            )

        uploads = []
        total_bytes = 0

        for file, role in files_to_read:
            remaining_bytes = MAX_BATCH_BYTES - total_bytes

            read_limit = min(
                MAX_UPLOAD_BYTES,
                remaining_bytes,
            )

            content = file.file.read(read_limit + 1)

            if len(content) > read_limit:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        "Una imagen supera los 10 MiB "
                        "o el conjunto supera los 40 MiB."
                    ),
                )

            total_bytes += len(content)

            uploads.append(
                MediaUpload(
                    content=content,
                    role=role,
                )
            )

        try:
            return save_media_batch(
                submission_directory,
                uploads,
            )

        except MediaAlreadyExistsError as error:
            raise HTTPException(
                status_code=409,
                detail=str(error),
            ) from error

        except InvalidMediaError as error:
            raise HTTPException(
                status_code=422,
                detail=str(error),
            ) from error

        except OSError as error:
            raise HTTPException(
                status_code=500,
                detail=(
                    "No se han podido guardar las imágenes. "
                    "Inténtalo de nuevo."
                ),
            ) from error

    return router