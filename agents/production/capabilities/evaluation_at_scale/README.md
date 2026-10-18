# Evaluation at scale

## POC

Run `python -m agents.production.capabilities.evaluation_at_scale.main --demo`. It evaluates synthetic cases concurrently with a bounded thread pool and reports pass rate and p50/p95 runtime.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | JSONL fixtures, Python `concurrent.futures`, deterministic metrics | Stable case IDs and reproducible baseline |
| Prototype | pytest, Ragas/DeepEval, LangSmith datasets/evaluators, task queue | Versioned runs, bounded concurrency, error capture, human labels |
| Enterprise | Distributed workers, object storage, evaluation service APIs, CI/CD | Sharding, idempotency, cost limits, access controls, statistical release gates |

Scale only after validating metric quality on human-labeled examples. Record model, prompt, dataset, and evaluator versions so results can be reproduced.
