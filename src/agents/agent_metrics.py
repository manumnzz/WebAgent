
from dataclasses import dataclass


@dataclass
class AgentMetrics:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    api_duration_seconds: float = 0.0
    api_calls: int = 0
    calls_without_usage: int = 0

    def record(self, usage, duration: float) -> None:
        self.api_calls += 1
        self.api_duration_seconds += duration

        if usage is None:
            self.calls_without_usage += 1
            return

        self.input_tokens += usage.input_tokens or 0
        self.output_tokens += usage.output_tokens or 0

        input_details = getattr(
            usage, "input_tokens_details", None
        )

        if input_details is not None:
            self.cached_input_tokens += (
                getattr(input_details, "cached_tokens", 0) or 0
            )

        output_details = getattr(
            usage, "output_tokens_details", None
        )

        if output_details is not None:
            self.reasoning_tokens += (
                getattr(output_details, "reasoning_tokens", 0) or 0
            )

    @property
    def uncached_input_tokens(self) -> int:
        return self.input_tokens - self.cached_input_tokens

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "uncached_input_tokens": self.uncached_input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "api_duration_seconds": round(
                self.api_duration_seconds, 3
            ),
            "api_calls": self.api_calls,
            "calls_without_usage": self.calls_without_usage,
        }
