"""Evaluate a synthetic dataset with bounded local concurrency."""

from concurrent.futures import ThreadPoolExecutor
import json
import statistics
import sys
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    case_id: str
    expected: str
    actual: str


CASES = tuple(
    Case(f"capital-{index:03}", expected, actual)
    for index, (expected, actual) in enumerate(
        [
            ("canberra", "Canberra"),
            ("tokyo", "Tokyo"),
            ("lisbon", "Lisbon"),
            ("helsinki", "Helsinki"),
            ("nairobi", "Nairobi"),
            ("ottawa", "Ottawa"),
        ],
        start=1,
    )
)


def evaluate(case: Case) -> tuple[dict[str, object], float]:
    started = time.perf_counter()
    passed = case.expected.casefold() in case.actual.casefold()
    duration_ms = (time.perf_counter() - started) * 1_000
    return (
        {"case_id": case.case_id, "passed": passed},
        duration_ms,
    )


def run_batch(max_workers: int = 4) -> dict[str, object]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        completed = list(executor.map(evaluate, CASES))
    results = [result for result, _ in completed]
    durations = sorted(duration for _, duration in completed)
    passed = sum(result["passed"] is True for result in results)
    return {
        "workers": max_workers,
        "total": len(results),
        "passed": passed,
        "pass_rate": passed / len(results) if results else 0.0,
        "latency_ms_p50": statistics.median(durations) if durations else 0.0,
        "latency_ms_p95": durations[min(len(durations) - 1, int(len(durations) * 0.95))]
        if durations
        else 0.0,
        "cases": results,
    }


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to evaluate the built-in synthetic dataset.")
    print(json.dumps(run_batch(), indent=2))


if __name__ == "__main__":
    main()
