"""Emit redacted structured events and a small in-process metrics summary."""

import json
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass, field

SECRET_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")


def redact(text: str) -> str:
    return SECRET_PATTERN.sub("[REDACTED]", text)


@dataclass
class RequestMetrics:
    requests: Counter[str] = field(default_factory=Counter)
    durations_ms: list[float] = field(default_factory=list)

    def observe(self, status: str, duration_ms: float) -> None:
        self.requests[status] += 1
        self.durations_ms.append(duration_ms)

    def summary(self) -> dict[str, object]:
        return {
            "requests_total": sum(self.requests.values()),
            "errors_total": self.requests["error"],
            "latency_ms_average": (
                sum(self.durations_ms) / len(self.durations_ms)
                if self.durations_ms
                else 0.0
            ),
        }


def demo() -> dict[str, object]:
    metrics = RequestMetrics()
    events = []
    for request_id, content in (
        ("req-001", "answer created"),
        ("req-002", "provider returned an error"),
    ):
        started = time.perf_counter()
        status = "error" if "error" in content else "ok"
        elapsed_ms = (time.perf_counter() - started) * 1_000
        metrics.observe(status, elapsed_ms)
        events.append(
            {
                "event": "agent_request",
                "request_id": request_id,
                "status": status,
                "message": redact(content + " sk-testSecret12345"),
                "duration_ms": round(elapsed_ms, 3),
            }
        )
    return {"events": events, "metrics": metrics.summary()}


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to emit sample events and metrics.")
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
