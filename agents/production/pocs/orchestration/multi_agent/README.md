# Multi-agent Graph POC

Runs the existing bounded planner -> specialist -> reviewer graph with an in-memory checkpointer. The graph has three sequential model calls, no tools, and no autonomous routing.

## Run

```powershell
python -m venv .venv-multi-agent
.\.venv-multi-agent\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\orchestration\multi_agent\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
$env:MODEL_NAME = "openai:gpt-4o-mini"
python -m agents.production.pocs.orchestration.multi_agent.main "Compare a modular monolith with microservices."
```

The model string uses LangChain's `provider:model` format. Set the credential environment variable required by the selected provider and change `MODEL_NAME` accordingly.

This is an orchestration demo, not a claim that adding agents improves quality. Compare its answer, latency, and cost to a one-call baseline before adopting it.
