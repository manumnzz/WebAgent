
import json
import os
import tempfile
from pathlib import Path

from agents.cost_calculator import calculate_agent_cost
from agents.model_pricing import PRICING_DATE

from agents.agent_metrics import AgentMetrics


def save_agent_metrics(
    path: Path,
    agent_name: str,
    model: str,
    metrics: AgentMetrics,
) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        report = json.loads(path.read_text(encoding="utf-8"))
    else:
        report = {"agents": {}}

    agent_runs = report["agents"].setdefault(agent_name, [])

    cost = calculate_agent_cost(model, metrics)

    agent_runs.append({
        "model": model,
        **metrics.to_dict(),
        "estimated_cost_usd": (
            str(cost) if cost is not None else None
        ),
        "pricing_date": PRICING_DATE,
        "pricing_mode": "standard",
    })

    # Escritura atómica para evitar archivos incompletos.
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(report, temporary, indent=2)
            temporary.write("\n")

        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
