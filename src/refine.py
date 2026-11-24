import argparse

from dotenv import load_dotenv


def main():
    load_dotenv()
    from projects.repair import repair_project
    from projects.workspace import build_project_workspace

    parser = argparse.ArgumentParser(
        description="Refina una copia de una web mediante feedback humano.",
    )
    parser.add_argument("--source-project-id", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--feedback", required=True)
    args = parser.parse_args()

    try:
        report = repair_project(
            build_project_workspace(args.source_project_id),
            build_project_workspace(args.project_id),
            feedback=args.feedback,
        )
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))

    print("\n=== REFINEMENT REPORT ===")
    print(report.model_dump_json(indent=2))
    print(f"\nProyecto disponible: {report.project_id}")
    raise SystemExit(0 if report.validation.is_valid else 1)


if __name__ == "__main__":
    main()
