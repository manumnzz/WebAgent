import argparse

from dotenv import load_dotenv

from projects.repair import repair_project
from projects.workspace import build_project_workspace


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Repara una copia de una web existente.",
    )

    parser.add_argument(
        "--source-project-id",
        required=True,
    )

    parser.add_argument(
        "--project-id",
        required=True,
        help="Identificador nuevo para la copia.",
    )

    args = parser.parse_args()

    try:
        source = build_project_workspace(
            args.source_project_id,
        )

        destination = build_project_workspace(
            args.project_id,
        )

        report = repair_project(
            source,
            destination,
        )

    except (OSError, ValueError) as error:
        parser.error(str(error))

    print("\n=== REPAIR REPORT ===")
    print(report.model_dump_json(indent=2))

    print(
        f"\nProyecto disponible: {report.project_id}"
    )

    raise SystemExit(
        0 if report.validation.is_valid else 1
    )


if __name__ == "__main__":
    main()