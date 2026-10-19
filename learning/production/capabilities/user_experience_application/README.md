# User experience and application layer

## POC

Install the shared production dependencies, then run:

```powershell
python -m pip install -r agents\production\requirements.txt
python -m agents.production.capabilities.user_experience_application.main --demo
python -m uvicorn agents.production.capabilities.user_experience_application.main:app --reload
```

The FastAPI sample exposes a typed `/v1/chat` request/response API and `/health`. Demo responses are deterministic and make no model call.

## Maturity path

| Stage | Tools, frameworks, and APIs | Add |
|---|---|---|
| Basic POC | FastAPI, Pydantic, Swagger/OpenAPI | Typed input/output and clear errors |
| Prototype | React/Next.js or existing UI, SSE/WebSockets, OIDC | Streaming, sessions, cancellations, feedback |
| Enterprise | API gateway, OIDC/Entra ID, BFF, localization/accessibility analytics | RBAC, tenant boundaries, audit, rate limits, backward-compatible API versioning |

Do not trust tenant or user IDs supplied in request bodies. Derive identity from verified tokens and enforce authorization server-side.
