import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"


def execute(arguments, *, environment=None):
    os.chdir(PROJECT_ROOT)

    env = os.environ.copy()

    if environment:
        env.update(environment)

    os.execvpe(
        str(PYTHON),
        [str(PYTHON), *arguments],
        env,
    )


def choose(paths, *, title, label):
    if not paths:
        raise SystemExit("No hay elementos disponibles.")

    print(f"\n{title}\n")

    for number, path in enumerate(paths, start=1):
        print(f"  {number}. {label(path)}")

    print("\n  0. Cancelar\n")

    while True:
        answer = input("Elige un número: ").strip()

        if answer == "0":
            raise SystemExit(0)

        if answer.isdigit() and 1 <= int(answer) <= len(paths):
            return paths[int(answer) - 1]

        print("Selecciona uno de los números de la lista.")


def submission_label(path):
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
        name = content.get("business_name") or "Sin nombre"
    except (OSError, ValueError, AttributeError):
        name = "Archivo pendiente de revisar"

    return f"{name} — {path.relative_to(PROJECT_ROOT)}"


def generate():
    paths = list(
        (PROJECT_ROOT / "data" / "intake").glob(
            "*/project_input.json"
        )
    )

    configuration_input = (
        PROJECT_ROOT / "config" / "project_input.json"
    )

    if configuration_input.is_file():
        paths.append(configuration_input)

    paths.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    selected = choose(
        paths,
        title="Encargos disponibles",
        label=submission_label,
    )

    suggested_id = (
        f"web-{datetime.now():%Y%m%d}-{uuid4().hex[:8]}"
    )

    project_id = input(
        f"\nNombre de la nueva salida [{suggested_id}]: "
    ).strip() or suggested_id

    print(f"\nGenerando proyecto: {project_id}", flush=True)
    print("Esta operación consume llamadas al modelo.\n", flush=True)

    execute(
        [
            "src/main.py",
            "--input",
            str(selected),
            "--project-id",
            project_id,
        ]
    )


def serve_website():
    projects_directory = PROJECT_ROOT / "output" / "projects"

    paths = [
        path
        for path in projects_directory.glob("*")
        if path.is_dir()
        and (path / "website" / "index.html").is_file()
    ]

    paths.sort(
        key=lambda path: (
            path / "website" / "index.html"
        ).stat().st_mtime,
        reverse=True,
    )

    selected = choose(
        paths,
        title="Webs generadas",
        label=lambda path: path.name,
    )

    print(
        f"\nProyecto: {selected.name}\n"
        "Web: http://127.0.0.1:8002/\n"
        "Detener: Ctrl+C\n",
        flush=True,
    )

    execute(
        [
            "-m",
            "uvicorn",
            "api.main:create_project_app",
            "--factory",
            "--app-dir",
            "src",
            "--reload",
            "--port",
            "8002",
        ],
        environment={
            "WEBAGENT_PROJECT_ID": selected.name,
        },
    )


def main():
    parser = argparse.ArgumentParser(
        description="Comandos de desarrollo de WebAgent.",
    )

    parser.add_argument(
        "command",
        choices=[
            "ayuda",
            "formulario",
            "generar",
            "web",
            "test",
        ],
        nargs="?",
        default="ayuda",
    )

    command = parser.parse_args().command

    if command == "generar":
        generate()

    elif command == "web":
        serve_website()

    elif command == "formulario":
        print(
            "\nFormulario: http://127.0.0.1:8001/\n"
            "Detener: Ctrl+C\n",
            flush=True,
        )

        execute(
            [
                "-m",
                "uvicorn",
                "intake.api:app",
                "--app-dir",
                "src",
                "--reload",
                "--port",
                "8001",
            ]
        )

    elif command == "test":
        execute(
            [
                "-m",
                "pytest",
                "src/tests",
                "-q",
                "-p",
                "no:cacheprovider",
            ]
        )

    else:
        print(
            "\nComandos de WebAgent:\n\n"
            "  make formulario  Levantar el formulario\n"
            "  make generar     Elegir encargo y generar web\n"
            "  make web         Elegir y servir una web\n"
            "  make test        Ejecutar los tests\n"
        )


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelado.")
        raise SystemExit(0)