# Observability and monitoring

## POC

Run `python -m agents.production.capabilities.observability_monitoring.main --demo`. It emits structured JSON events, redacts a simple demo key pattern, and reports a request counter, errors, and latency.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | Python logging, counters, monotonic timers | Correlatable request IDs, status and latency |
| Prototype | OpenTelemetry SDK/exporters, Prometheus, Grafana, LangSmith/Langfuse/Phoenix | Traces, dashboards, LLM/token/tool spans |
| Enterprise | OpenTelemetry Collector, managed metrics/logging/tracing, SIEM, alerting | SLOs, sampling, access controls, redaction, retention, on-call and incident playbooks |

Do not log raw prompts, outputs, credentials, or personal data by default. Demonstration redaction is not a complete DLP system; define telemetry schemas, privacy review, retention, and access policy.
