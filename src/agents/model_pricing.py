
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ModelPricing:
    input_per_million: Decimal
    cached_input_per_million: Decimal
    output_per_million: Decimal


# Precios orientativos en USD por millón de tokens.
# Modalidad Standard. Revisar antes de cada benchmark.
PRICING_DATE = "2026-11-22"

MODEL_PRICES = {
    "gpt-5.6-luna": ModelPricing(
        Decimal("0.20"),
        Decimal("0.02"),
        Decimal("1.20"),
    ),
    "gpt-6-luna": ModelPricing(
        Decimal("0.05"),
        Decimal("0.005"),
        Decimal("0.25"),
    ),
    "gpt-6.1-terra": ModelPricing(
        Decimal("0.50"),
        Decimal("0.025"),
        Decimal("2.50"),
    ),
    "gpt-6.2-sol": ModelPricing(
        Decimal("1.00"),
        Decimal("0.05"),
        Decimal("5.00"),
    ),
    "gpt-6.2-astra": ModelPricing(
        Decimal("4.00"),
        Decimal("0.20"),
        Decimal("20.00"),
    ),
}


def get_model_pricing(model: str) -> ModelPricing | None:
    return MODEL_PRICES.get(model)
