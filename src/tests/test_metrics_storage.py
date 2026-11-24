
import json

from agents.agent_metrics import AgentMetrics
from agents.metrics_storage import save_agent_metrics


def test_save_metrics_creates_json(tmp_path):
    path = tmp_path / "metrics.json"

    metrics = AgentMetrics(
        input_tokens=1000,
        output_tokens=500,
        reasoning_tokens=100,
        api_duration_seconds=2.5,
        api_calls=1,
    )

    save_agent_metrics(
        path=path,
        agent_name="ux_agent",
        model="gpt-5.6-luna",
        metrics=metrics,
    )

    report = json.loads(path.read_text(encoding="utf-8"))

    assert report["agents"]["ux_agent"][0]["model"] == "gpt-5.6-luna"
    assert report["agents"]["ux_agent"][0]["input_tokens"] == 1000
    assert report["agents"]["ux_agent"][0]["output_tokens"] == 500


def test_multiple_runs_are_preserved(tmp_path):
    path = tmp_path / "metrics.json"

    for tokens in [100, 200, 300]:
        save_agent_metrics(
            path=path,
            agent_name="developer_agent",
            model="gpt-5.6-luna",
            metrics=AgentMetrics(
                input_tokens=tokens,
                output_tokens=50,
                api_calls=1,
            ),
        )

    report = json.loads(path.read_text(encoding="utf-8"))
    runs = report["agents"]["developer_agent"]

    assert len(runs) == 3
    assert sum(run["input_tokens"] for run in runs) == 600


def test_different_agents_are_preserved(tmp_path):
    path = tmp_path / "metrics.json"

    for name in ["business_agent", "design_agent"]:
        save_agent_metrics(
            path=path,
            agent_name=name,
            model="gpt-5.6-luna",
            metrics=AgentMetrics(api_calls=1),
        )

    report = json.loads(path.read_text(encoding="utf-8"))

    assert set(report["agents"]) == {
        "business_agent",
        "design_agent",
    }
