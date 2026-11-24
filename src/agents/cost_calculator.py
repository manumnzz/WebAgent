
from decimal import Decimal

from agents.agent_metrics import AgentMetrics
from agents.model_pricing import get_model_pricing


MILLION = Decimal("1000000")


def calculate_agent_cost(
    model: str,
    metrics: AgentMetrics,
) -> Decimal | None:
    """
    Coste estimado en USD según tokens y tarifas Standard.

    Devuelve None si no hay precio conocido o faltan
    datos de uso de alguna llamada.
    """
    pricing = get_model_pricing(model)

    if pricing is None or metrics.calls_without_usage:
        return None

    if not 0 <= metrics.cached_input_tokens <= metrics.input_tokens:
        raise ValueError("Los tokens cacheados no son válidos.")

    if min(
        metrics.input_tokens,
        metrics.output_tokens,
        metrics.reasoning_tokens,
    ) < 0:
        raise ValueError("Los tokens no pueden ser negativos.")

    input_cost = (
        Decimal(metrics.uncached_input_tokens)
        * pricing.input_per_million
        / MILLION
    )

    cached_cost = (
        Decimal(metrics.cached_input_tokens)
        * pricing.cached_input_per_million
        / MILLION
    )

    output_cost = (
        Decimal(metrics.output_tokens)
        * pricing.output_per_million
        / MILLION
    )

    return input_cost + cached_cost + output_cost
