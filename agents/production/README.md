# Production Agent API Example

A runnable starting point for a typed FastAPI service using Pydantic, LangGraph, Deep Agents, and PostgreSQL checkpoints.

## Included workflows

- `POST /agent`: a finite planner -> specialist -> reviewer LangGraph pipeline. The graph structure is explicit, and its agents have no tools.
- `POST /deep-agent`: a separate Deep Agents workflow wrapped in a LangGraph graph so its outer conversation state uses the same PostgreSQL checkpointer.
- `GET /health`: liveness endpoint. PostgreSQL, model configuration, and checkpoint setup are verified during application startup.

For categorized, isolated POCs covering multi-agent orchestration, Deep Agents, LiteLLM, other gateways, LangSmith, Langfuse, and Arize Phoenix, see [Production Agent POCs](pocs/README.md).

For evaluation, safety, memory, observability, cost, UX, infrastructure, prompts, and dataset practices, see [Production Agent Capabilities](capabilities/README.md).

Both request workflows accept a UUID `thread_id`. The checkpointer stores graph state in PostgreSQL under a namespace derived from the authenticated principal and workflow. Reuse a thread ID on the same endpoint to continue its conversation; generate a new one to start a separate conversation.

## Run locally

Create a virtual environment, install the dependencies, configure `.env` from `.env.example`, and ensure PostgreSQL is running with the database and credentials in `POSTGRES_DSN`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r agents\production\requirements.txt
Copy-Item agents\production\.env.example .env
# Edit .env with real credentials; never commit it.
python -m uvicorn agents.production.app:app --reload
```

The PostgreSQL checkpointer creates its tables at startup. Open `/docs`, authorize with the configured bearer token, and submit a JSON body such as:

```json
{
  "question": "Summarize the tradeoffs between a modular monolith and microservices.",
  "thread_id": "9b3b7a61-05b8-4c94-95c8-c247aee3426a"
}
```

For PowerShell, set the token and call an endpoint:

```powershell
$token = "the-API_BEARER_TOKEN-from-your-local-.env"
$body = @{
  question = "Summarize the tradeoffs between a modular monolith and microservices."
  thread_id = "9b3b7a61-05b8-4c94-95c8-c247aee3426a"
} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/agent -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" -Body $body
```

Use `/deep-agent` instead to run the Deep Agents path.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s agents\production -p "test_*.py" -v
```

The tests use deterministic fake chat models and an in-memory checkpointer; they do not call a model provider or require a running PostgreSQL server.

## Before production

This is an instructional service scaffold, not a complete production deployment. The shared bearer token is a demo authentication mechanism: replace it with your OIDC provider, validate user identity and tenant/resource permissions, and derive thread namespaces from verified claims. Do not allow callers to access another principal's thread.

Add migrations and application data repositories for business records; the LangGraph checkpointer persists workflow state, not business data or a complete audit trail. Add secret-manager integration, TLS and database network controls, request rate/cost limits, timeouts, structured redacted logs, tracing, metrics, retries, graceful shutdown, and deployment health/readiness probes. Define retention and deletion for checkpoint rows.

The multi-agent path has a fixed maximum of three model calls and no tools. The Deep Agents path is a separate example and does not receive external tools. Keep these limits and permissions explicit when extending workflows; require approval for consequential actions and enforce authorization in application code, never in model prompts.
