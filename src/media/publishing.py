from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from media.models import WebsiteMediaAsset
from media.storage import load_media_manifest
from projects.workspace import ProjectWorkspace


def publish_submission_media(
    submission_directory: str | Path,
    workspace: ProjectWorkspace,
) -> list[WebsiteMediaAsset]:
    submission_directory = Path(
        submission_directory
    ).resolve()

    manifest = load_media_manifest(
        submission_directory,
    )

    if not manifest.assets:
        return []

    source_directory = (
        submission_directory / "media"
    ).resolve()

    # Primero comprobar todas las imágenes.
    for asset in manifest.assets:
        source_path = (
            source_directory / asset.filename
        ).resolve()

        if not source_path.is_relative_to(source_directory):
            raise ValueError(
                "Un recurso apunta fuera de la carpeta multimedia."
            )

        if not source_path.is_file():
            raise FileNotFoundError(
                f"No existe la imagen del manifiesto: "
                f"{asset.filename}"
            )

    # Este bloque está fuera del primer for.
    destination_directory = (
        workspace.website_directory / "assets"
    )

    if destination_directory.exists():
        raise FileExistsError(
            "El workspace ya tiene una carpeta de assets."
        )

    workspace.website_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    published_assets = []

    with TemporaryDirectory(
        prefix=".assets-",
        dir=workspace.website_directory,
    ) as temporary_directory:
        staged_directory = (
            Path(temporary_directory) / "prepared"
        )
        staged_directory.mkdir()

        # Copiar mientras la carpeta temporal existe.
        for asset in manifest.assets:
            source_path = source_directory / asset.filename
            destination_path = staged_directory / asset.filename

            copyfile(
                source_path,
                destination_path,
            )

            published_assets.append(
                WebsiteMediaAsset(
                    **asset.model_dump(),
                    path=asset.public_path,
                )
            )

        # Confirmar antes de salir del with.
        staged_directory.rename(destination_directory)

    return published_assets