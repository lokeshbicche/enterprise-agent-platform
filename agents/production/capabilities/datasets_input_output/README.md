# Datasets: inputs and outputs

## POC

Run `python -m agents.production.capabilities.datasets_input_output.main --demo`. It loads the versioned synthetic JSONL fixture, validates record shape and types, and writes example input/output records to stdout without exposing user data.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | JSONL, Python dataclasses, schema checks | Stable IDs, explicit expected output and labels |
| Prototype | Pydantic/JSON Schema, object storage, DVC or lakeFS | Dataset version, lineage, train/eval split, validation |
| Enterprise | Governed data catalog, IAM, encrypted object storage, evaluation APIs | Consent, PII handling, retention/deletion, approval, reproducible snapshots |

Treat prompts and outputs as potentially sensitive. Keep synthetic fixtures in source control; store real evaluation datasets in approved restricted storage with documented purpose and retention.
