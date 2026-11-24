
import argparse
import json
from decimal import Decimal
from pathlib import Path


def build_cost_report(metrics_path: Path) -> dict:
    data = json.loads(
        metrics_path.read_text(encoding="utf-8")
    )

    agents = {}
    total_cost = Decimal("0")
    total_calls = 0
    complete = True

    for name, runs in data.get("agents", {}).items():
        agent_cost = Decimal("0")
        agent_calls = 0
        agent_complete = True

        for run in runs:
            agent_calls += run.get("api_calls", 0)

            cost = run.get("estimated_cost_usd")

            if cost is None:
                agent_complete = False
                complete = False
                continue

            agent_cost += Decimal(str(cost))

        agents[name] = {
            "cost_usd": str(agent_cost),
            "api_calls": agent_calls,
            "complete": agent_complete,
            "executions": len(runs),
        }

        total_cost += agent_cost
        total_calls += agent_calls

    return {
        "total_cost_usd": str(total_cost),
        "total_api_calls": total_calls,
        "complete": complete,
        "agents": agents,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Informe económico de WebAgent."
    )

    parser.add_argument(
        "metrics_path",
        type=Path,
        help="Ruta al archivo metrics.json",
    )

    args = parser.parse_args()

    report = build_cost_report(args.metrics_path)

    print("\n=== COSTE DE WEBAGENT ===\n")

    for name, data in report["agents"].items():
        status = "" if data["complete"] else " (parcial)"
        print(
            f"{name:20}"
            f"${Decimal(data['cost_usd']):.6f}"
            f" | {data['api_calls']} llamadas"
            f"{status}"
        )

    print("\n----------------------------")
    print(
        "TOTAL ESTIMADO:",
        f"${Decimal(report['total_cost_usd']):.6f}",
    )
    print("LLAMADAS API:", report["total_api_calls"])

    if not report["complete"]:
        print(
            "\nAVISO: El total es parcial. "
            "Hay ejecuciones sin coste calculable."
        )


if __name__ == "__main__":
    main()
