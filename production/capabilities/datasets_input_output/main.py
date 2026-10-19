"""Load and validate the small versioned JSONL fixture."""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DATASET_PATH = Path(__file__).with_name("sample_dataset.jsonl")


@dataclass(frozen=True)
class DatasetRecord:
    record_id: str
    input: str
    expected_output: str
    dataset_version: str


def parse_record(value: Any, line_number: int) -> DatasetRecord:
    if not isinstance(value, dict):
        raise ValueError(f"Line {line_number}: expected a JSON object.")
    required = {"record_id", "input", "expected_output", "dataset_version"}
    if set(value) != required:
        raise ValueError(
            f"Line {line_number}: expected keys {sorted(required)}; got {sorted(value)}."
        )
    if not all(isinstance(value[key], str) and value[key].strip() for key in required):
        raise ValueError(f"Line {line_number}: all fields must be non-empty strings.")
    return DatasetRecord(**value)


def load_dataset(path: Path = DATASET_PATH) -> list[DatasetRecord]:
    records = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = parse_record(json.loads(line), line_number)
        if record.record_id in seen_ids:
            raise ValueError(f"Line {line_number}: duplicate record_id {record.record_id!r}.")
        seen_ids.add(record.record_id)
        records.append(record)
    return records


def demo() -> dict[str, object]:
    records = load_dataset()
    return {
        "dataset_version": records[0].dataset_version if records else None,
        "record_count": len(records),
        "records": [record.__dict__ for record in records],
    }


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run with --demo to load and validate the sample JSONL dataset.")
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
