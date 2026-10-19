# Prompt engineering

## POC

Run `python -m agents.production.capabilities.prompt_engineering.main --demo`. It renders a versioned prompt from typed task/context values, labels retrieved text as untrusted evidence, and checks for required prompt sections.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | Versioned templates, explicit instructions, deterministic tests | Separate instructions, context, and output format |
| Prototype | LangChain prompt templates, provider structured-output APIs, golden dataset | Compare prompt versions on task-specific cases |
| Enterprise | Prompt registry/approval workflow, LangSmith Prompt Hub or equivalent, eval CI | Ownership, staged rollout, rollback, injection tests, audit and deprecation |

Prompt instructions are not security controls. Validate structured outputs and enforce permissions in application code.
