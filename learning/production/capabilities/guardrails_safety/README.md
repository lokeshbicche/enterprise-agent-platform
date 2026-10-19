# Guardrails and safety

## POC

Run `python -m agents.production.capabilities.guardrails_safety.main --demo`. The sample validates request length and a narrow tool allowlist, then flags a demo output containing a fake credential pattern. It does not call an LLM.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | Typed request validation, explicit allowlists, unit tests | Reject malformed requests and deny-by-default tool names |
| Prototype | Pydantic, NeMo Guardrails or Guardrails AI, provider moderation APIs | Threat model, prompt-injection tests, output checks, human approval |
| Enterprise | OIDC/IAM, policy engine (OPA), DLP/content safety APIs, audit service | Per-tenant authorization at tool boundaries, policy ownership, escalation, red-team and incident workflows |

The POC's string checks are illustrative only. Prompt wording, regular expressions, and model moderation are not authorization. Never give a model authority that the authenticated application user lacks.
