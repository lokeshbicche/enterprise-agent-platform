# Context and memory

## POC

Run `python -m agents.production.capabilities.context_memory.main --demo`. It uses SQLite in-memory storage to keep a session's recent messages and a small set of explicit facts, then builds a bounded context window.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | Bounded in-memory history, SQLite, explicit user facts | Session IDs and context limits |
| Prototype | LangGraph checkpointers, PostgreSQL/Redis, vector retrieval | Durable state, retrieval citations, expiry and deletion |
| Enterprise | Tenant-isolated stores, IAM, encryption/KMS, managed databases | Consent, retention schedules, subject deletion, access audit, migration and recovery tests |

Separate short-term conversation state, durable user-approved memory, and retrieved knowledge. Retrieved text is untrusted input, not policy. Establish retention and deletion behavior before persisting real user data.
