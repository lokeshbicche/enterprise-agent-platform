"""Demonstrate approximate LLM cost estimation and a tiny TTL cache."""

import json
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRate:
    input_per_million: float
    output_per_million: float


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    rate: ModelRate,
) -> float:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts must be non-negative.")
    return (
        input_tokens * rate.input_per_million
        + output_tokens * rate.output_per_million
    ) / 1_000_000


class TTLCache:
    def __init__(self, ttl_seconds: float, clock=time.monotonic) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive.")
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._values: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> str | None:
        entry = self._values.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if self._clock() >= expires_at:
            del self._values[key]
            return None
        return value

    def set(self, key: str, value: str) -> None:
        self._values[key] = (self._clock() + self._ttl_seconds, value)


def demo() -> dict[str, object]:
    cache = TTLCache(ttl_seconds=60)
    cache.set("query-hash-001", "Cached, previously evaluated answer")
    return {
        "estimated_cost_usd": round(
            estimate_cost(
                1_000,
                250,
                ModelRate(input_per_million=0.15, output_per_million=0.60),
            ),
            8,
        ),
        "cache_result": cache.get("query-hash-001"),
        "cache_miss": cache.get("unknown-query"),
        "note": "Example rates only; check the provider's current pricing and usage.",
    }


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to estimate cost and inspect the TTL cache.")
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
