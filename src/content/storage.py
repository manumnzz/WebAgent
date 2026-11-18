import json

from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from content.models import WebsiteContent
from content.presentation import RUNTIME_NAME
from projects.workspace import ProjectWorkspace


def save_website_content(
    content: WebsiteContent,
    path: str | Path,
) -> None:
    """
    Guarda el contenido editable de forma atómica.
    """

    destination = Path(path)

    # Validamos el modelo antes de escribir.
    serialized = content.model_dump_json(indent=2)

    WebsiteContent.model_validate_json(serialized)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with TemporaryDirectory(
        dir=destination.parent,
        prefix="website-content-",
    ) as temporary_directory:

        temporary_path = (
            Path(temporary_directory) / "content.json"
        )

        temporary_path.write_text(
            serialized,
            encoding="utf-8",
        )

        temporary_path.replace(destination)


def load_website_content(
    path: str | Path,
) -> WebsiteContent:
    """
    Recupera y valida el contenido editable.
    """

    source = Path(path)

    if not source.is_file():
        raise FileNotFoundError(
            f"No existe el contenido de la web: {source}"
        )

    return WebsiteContent.model_validate_json(
        source.read_text(encoding="utf-8")
    )


def validate_content_assets(content: WebsiteContent, website_root: Path) -> None:
    root = website_root.resolve()
    for image in content.gallery:
        path = (root / image.path).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"La imagen de la galería no existe en esta web: {image.path}")


def publish_content_edit(workspace: ProjectWorkspace, draft: Path) -> None:
    destination = workspace.website_content_path
    if draft.resolve() == destination.resolve():
        raise ValueError("Edita una copia de content.json y pásala como borrador.")

    if not (workspace.website_directory / RUNTIME_NAME).is_file():
        raise ValueError("La web aún no tiene activado el contenido editable.")

    existing = load_website_content(destination)
    payload = json.loads(draft.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("El borrador debe contener un objeto JSON.")

    existing_ids = {service.id for service in existing.services}
    services = payload.get("services", [])
    if isinstance(services, list):
        for entry in services:
            if not isinstance(entry, dict):
                continue
            if "id" not in entry:
                entry["id"] = uuid4().hex
            elif isinstance(entry["id"], str) and entry["id"] not in existing_ids:
                raise ValueError("Conserva el id de cada servicio existente y omítelo en los nuevos.")

    candidate = WebsiteContent.model_validate(payload)
    validate_content_assets(candidate, workspace.website_directory)
    save_website_content(candidate, destination)
