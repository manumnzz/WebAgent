import argparse
from pathlib import Path

from content.storage import publish_content_edit
from projects.workspace import build_project_workspace


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Valida y publica una edición de content.json sin regenerar la web.",
    )
    parser.add_argument("--project-id", required=True)
    parser.add_argument("draft", type=Path, help="Ruta de una copia editada de content.json.")
    arguments = parser.parse_args()

    try:
        workspace = build_project_workspace(arguments.project_id)
        publish_content_edit(workspace, arguments.draft)
    except (OSError, ValueError) as error:
        parser.exit(1, f"No se ha publicado el contenido. {error}\n")

    print(f"Contenido publicado en {workspace.website_content_path}")


if __name__ == "__main__":
    main()
