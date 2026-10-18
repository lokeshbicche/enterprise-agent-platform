# Agent Production Capabilities

Ten categorized learning paths for building an agent from a local proof of concept (POC) toward an enterprise service. Every folder contains a runnable, bounded POC and a guide to appropriate tools, frameworks, and APIs at increasing maturity.

## Categories

1. [Evaluation and quality](evaluation_quality/README.md): task correctness, groundedness, regression, and human review.
2. [Guardrails and safety](guardrails_safety/README.md): input/output validation, policy enforcement, and review gates.
3. [Context and memory](context_memory/README.md): context windows, session history, durable memory, and retrieval.
4. [Observability and monitoring](observability_monitoring/README.md): traces, metrics, logs, alerts, and privacy.
5. [Evaluation at scale](evaluation_at_scale/README.md): reproducible datasets, parallel runs, scorecards, and CI.
6. [Cost and performance](cost_performance/README.md): budgets, latency, caching, model routing, and load tests.
7. [User experience and application layer](user_experience_application/README.md): typed API boundary, sessions, streaming, and UI.
8. [Infrastructure and scale](infrastructure_scale/README.md): containers, health checks, deployment, autoscaling, and recovery.
9. [Prompt engineering](prompt_engineering/README.md): versioned templates, constraints, examples, and regression.
10. [Datasets: inputs and outputs](datasets_input_output/README.md): versioned JSONL records, validation, lineage, and access controls.

## Suggested progression

- **Basic POC:** run the local demo with synthetic, non-sensitive data.
- **Prototype:** replace the demo logic with the selected model/API, add tests, evaluate a representative dataset, and instrument failure cases.
- **Enterprise:** enforce identity and tenant authorization, use approved managed services, define SLOs and retention, validate deployment and rollback, and require human review for consequential actions.

The progression tables in each folder list example tools and APIs; they are options, not mandatory dependencies. The POCs avoid model-provider calls unless a guide explicitly says otherwise. A demonstration rule or in-memory implementation is not a production safety guarantee or service-level claim.

## Run the offline examples

From the repository root:

```powershell
python -m agents.production.capabilities.evaluation_quality.main --demo
python -m agents.production.capabilities.guardrails_safety.main --demo
python -m agents.production.capabilities.context_memory.main --demo
python -m agents.production.capabilities.observability_monitoring.main --demo
python -m agents.production.capabilities.evaluation_at_scale.main --demo
python -m agents.production.capabilities.cost_performance.main --demo
python -m agents.production.capabilities.user_experience_application.main --demo
python -m agents.production.capabilities.prompt_engineering.main --demo
python -m agents.production.capabilities.datasets_input_output.main --demo
```

The infrastructure example builds/runs the user-experience service using Docker; see its guide. For focused offline checks:

```powershell
python -m unittest agents.production.capabilities.test_capabilities -v
```
