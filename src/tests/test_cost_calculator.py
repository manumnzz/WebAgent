
import json
from decimal import Decimal
from types import SimpleNamespace

import pytest

from agents.agent_metrics import AgentMetrics
from agents.cost_calculator import calculate_agent_cost
from agents.metrics_storage import save_agent_metrics
from agents.cost_report import build_cost_report


def make_usage(
    input_tokens,
    cached_tokens,
    output_tokens,
    reasoning_tokens=0,
):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_tokens_details=SimpleNamespace(
            cached_tokens=cached_tokens,
        ),
        output_tokens_details=SimpleNamespace(
            reasoning_tokens=reasoning_tokens,
        ),
    )


def test_uncached_input_tokens():
    metrics = AgentMetrics(
        input_tokens=1000,
        cached_input_tokens=250,
    )

    assert metrics.uncached_input_tokens == 750


def test_record_cached_tokens():
    metrics = AgentMetrics()

    metrics.record(
        make_usage(1000, 300, 500, 100),
        duration=2.0,
    )

    assert metrics.input_tokens == 1000
    assert metrics.cached_input_tokens == 300
    assert metrics.uncached_input_tokens == 700
    assert metrics.output_tokens == 500
    assert metrics.reasoning_tokens == 100


def test_cost_without_cache():
    metrics = AgentMetrics(
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )

    cost = calculate_agent_cost(
        "gpt-6-luna",
        metrics,
    )

    assert cost == Decimal("0.30")


def test_cost_with_cache():
    metrics = AgentMetrics(
        input_tokens=15_000,
        cached_input_tokens=5_000,
        output_tokens=4_000,
    )

    cost = calculate_agent_cost(
        "gpt-6.2-sol",
        metrics,
    )

    assert cost == Decimal("0.03025")


def test_reasoning_not_charged_twice():
    metrics = AgentMetrics(
        input_tokens=0,
        output_tokens=1_000_000,
        reasoning_tokens=500_000,
    )

    cost = calculate_agent_cost(
        "gpt-6-luna",
        metrics,
    )

    assert cost == Decimal("0.25")


def test_unknown_model_returns_none():
    metrics = AgentMetrics(
        input_tokens=1000,
        output_tokens=500,
    )

    assert calculate_agent_cost(
        "unknown-model",
        metrics,
    ) is None


def test_missing_usage_returns_unknown_cost():
    metrics = AgentMetrics(
        api_calls=1,
        calls_without_usage=1,
    )

    assert calculate_agent_cost(
        "gpt-6-luna",
        metrics,
    ) is None


def test_invalid_cached_tokens():
    metrics = AgentMetrics(
        input_tokens=100,
        cached_input_tokens=200,
    )

    with pytest.raises(ValueError):
        calculate_agent_cost("gpt-6-luna", metrics)


def test_metrics_storage_includes_cost(tmp_path):
    path = tmp_path / "metrics.json"

    save_agent_metrics(
        path=path,
        agent_name="design_agent",
        model="gpt-6-luna",
        metrics=AgentMetrics(
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            api_calls=1,
        ),
    )

    data = json.loads(path.read_text())

    run = data["agents"]["design_agent"][0]

    assert Decimal(run["estimated_cost_usd"]) == Decimal("0.30")
    assert run["pricing_mode"] == "standard"


def test_project_cost_report(tmp_path):
    path = tmp_path / "metrics.json"

    for agent in ["ux_agent", "design_agent"]:
        save_agent_metrics(
            path=path,
            agent_name=agent,
            model="gpt-6-luna",
            metrics=AgentMetrics(
                input_tokens=1_000_000,
                output_tokens=1_000_000,
                api_calls=1,
            ),
        )

    report = build_cost_report(path)

    assert Decimal(report["total_cost_usd"]) == Decimal("0.60")
    assert report["total_api_calls"] == 2
    assert report["complete"] is True


def test_report_detects_unknown_cost(tmp_path):
    path = tmp_path / "metrics.json"

    save_agent_metrics(
        path=path,
        agent_name="developer_agent",
        model="unknown-model",
        metrics=AgentMetrics(api_calls=1),
    )

    report = build_cost_report(path)

    assert report["complete"] is False
    assert report["agents"]["developer_agent"]["complete"] is False


def test_developer_repairs_accumulate(tmp_path):
    path = tmp_path / "metrics.json"

    for _ in range(3):
        save_agent_metrics(
            path=path,
            agent_name="developer_agent",
            model="gpt-6-luna",
            metrics=AgentMetrics(
                input_tokens=1_000_000,
                output_tokens=1_000_000,
                api_calls=1,
            ),
        )

    report = build_cost_report(path)

    assert Decimal(report["total_cost_usd"]) == Decimal("0.90")
    assert report["agents"]["developer_agent"]["executions"] == 3
    assert report["total_api_calls"] == 3
