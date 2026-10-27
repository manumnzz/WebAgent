"""Capture or improve an existing generation without regenerating the business contract."""

import argparse
from shutil import copytree
from uuid import uuid4

from dotenv import load_dotenv
from projects.workspace import build_project_workspace
from visual.capture import capture_site
from visual.pipeline import improve_visual


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Captura y mejora visual de WebAgent.")
    parser.add_argument("--source-project-id", required=True)
    parser.add_argument(
        "--project-id", help="Nombre NUEVO de la copia que se va a mejorar."
    )
    parser.add_argument("--improve", action="store_true")
    parser.add_argument("--max-attempts", type=int, choices=range(0, 4), default=2)
    args = parser.parse_args()
    try:
        source = build_project_workspace(args.source_project_id)
        if not args.improve:
            directory = source.root / "config" / "screenshots" / uuid4().hex[:12]
            report = capture_site(source.website_directory, directory)
            print(report.model_dump_json(indent=2))
            print(f"Capturas: {directory}")
            return
        if not args.project_id:
            parser.error("--improve requiere --project-id para trabajar en una copia.")
        destination = build_project_workspace(args.project_id)
        if destination.root.exists():
            raise FileExistsError("El proyecto de destino ya existe.")
        if not source.website_spec_path.is_file():
            raise FileNotFoundError("El proyecto original no tiene website_spec.json.")
        copytree(source.root, destination.root)
        report = improve_visual(destination, max_attempts=args.max_attempts)
        print(report.model_dump_json(indent=2))
        print(f"Proyecto: {destination.project_id}")
        raise SystemExit(0 if report.status == "passed" else 1)
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
