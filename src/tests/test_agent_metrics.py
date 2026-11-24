
from types import SimpleNamespace

import pytest

from agents.agent_metrics import AgentMetrics


def make_usage(input_tokens, output_tokens, reasoning_tokens=0):
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        output_tokens_details=SimpleNamespace(
            reasoning_tokens=reasoning_tokens,
        ),
    )


def test_metrics_start_at_zero():
    metrics = AgentMetrics()

    assert metrics.input_tokens == 0
    assert metrics.output_tokens == 0
    assert metrics.reasoning_tokens == 0
    assert metrics.api_calls == 0


def test_record_single_api_call():
    metrics = AgentMetrics()

    metrics.record(
        make_usage(1000, 500, 100),
        duration=2.5,
    )

    assert metrics.input_tokens == 1000
    assert metrics.output_tokens == 500
    assert metrics.reasoning_tokens == 100
    assert metrics.api_calls == 1
    assert metrics.api_duration_seconds == 2.5


def test_accumulate_multiple_calls():
    metrics = AgentMetrics()

    metrics.record(make_usage(1000, 500, 100), 2.0)
    metrics.record(make_usage(2000, 800, 200), 3.0)

    assert metrics.input_tokens == 3000
    assert metrics.output_tokens == 1300
    assert metrics.reasoning_tokens == 300
    assert metrics.api_calls == 2
    assert metrics.api_duration_seconds == 5.0


def test_missing_usage():
    metrics = AgentMetrics()

    metrics.record(None, duration=1.0)

    assert metrics.api_calls == 1
    assert metrics.input_tokens == 0
    assert metrics.output_tokens == 0


def test_reasoning_tokens_are_not_added_to_output():
    metrics = AgentMetrics()

    metrics.record(
        make_usage(1000, 500, 200),
        duration=1.0,
    )

    assert metrics.output_tokens == 500
    assert metrics.reasoning_tokens == 200
