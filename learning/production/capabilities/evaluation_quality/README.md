# Evaluation and quality

## POC

Run `python -m agents.production.capabilities.evaluation_quality.main --demo` for a tiny deterministic test set scored on exact match and required terms. It prints per-case results and an aggregate pass rate; no LLM or network is used.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | Python `unittest`, hand-written fixtures | Correctness checks and explicit pass criteria |
| Prototype | pytest, DeepEval or Ragas, model/provider APIs, human review | Representative cases, retrieval/faithfulness measures, failure analysis |
| Enterprise | LangSmith evaluations/datasets, Arize Phoenix, OpenTelemetry, CI/CD | Versioned evals, release gates, reviewer queues, drift and quality SLOs |

Scores are indicators, not proof of correctness. Calibrate automated judges against domain-expert labels and keep sensitive evaluation data access-controlled.
