# LangSmith LLM Gateway POC

Makes an OpenAI-compatible call through the LangSmith Gateway, authenticated with a workspace-scoped `LANGSMITH_API_KEY`. A workspace administrator must enable the gateway, configure provider secrets, and grant the key `gateway:invoke` and `workspaces:read` permissions first. The gateway is currently documented as beta.

## Run

```powershell
python -m venv .venv-langsmith-gateway
.\.venv-langsmith-gateway\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\model_gateways\langsmith_gateway\requirements.txt
$env:LANGSMITH_API_KEY = "your-workspace-scoped-key"
$env:LANGSMITH_GATEWAY_MODEL = "openai/gpt-4o-mini"
python -m agents.production.pocs.model_gateways.langsmith_gateway.main "Say hello in one sentence."
```

The endpoint below is the LangSmith Cloud US endpoint. Use your region's or deployment's gateway base URL when applicable. Model IDs use the provider-prefixed format supported by your workspace configuration.
