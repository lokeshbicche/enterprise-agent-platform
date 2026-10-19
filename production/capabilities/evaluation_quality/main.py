"""Small deterministic example of task-output evaluation."""

import json
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    expected: str
    required_terms: tuple[str, ...]
    actual: str


CASES = (
    EvaluationCase(
        "capital-001",
        "Canberra is the capital of Australia.",
        ("canberra",),
        "Canberra is the capital of Australia.",
    ),
    EvaluationCase(
        "capital-002",
        "The capital is Tokyo.",
        ("tokyo",),
        "The capital is Tokyo.",
    ),
    EvaluationCase(
        "capital-003",
        "Lisbon is the capital of Portugal.",
        ("lisbon",),
        "Lisbon is the capital of Portugal.",
    ),
)


def evaluate(case: EvaluationCase) -> dict[str, object]:
    actual = case.actual.strip().casefold()
    exact_match = case.expected.strip().casefold() == actual
    required_terms_present = all(term.casefold() in actual for term in case.required_terms)
    return {
        "case_id": case.case_id,
        "passed": exact_match and required_terms_present,
        "exact_match": exact_match,
        "required_terms_present": required_terms_present,
    }


def run_evaluation() -> dict[str, object]:
    results = [evaluate(case) for case in CASES]
    passed = sum(result["passed"] is True for result in results)
    return {
        "passed": passed,
        "total": len(results),
        "pass_rate": passed / len(results) if results else 0.0,
        "cases": results,
    }


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to score the built-in synthetic cases.")
    print(json.dumps(run_evaluation(), indent=2))


if __name__ == "__main__":
    main()
