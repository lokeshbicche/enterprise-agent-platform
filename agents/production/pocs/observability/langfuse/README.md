# Langfuse Tracing POC

Uses Langfuse's LangChain callback handler to capture an agent run. Supports Langfuse Cloud and self-hosted deployments; use the correct `LANGFUSE_BASE_URL` for your region or server.

## Run

```powershell
python -m venv .venv-langfuse
.\.venv-langfuse\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\observability\langfuse\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
$env:LANGFUSE_SECRET_KEY = "your-secret-key"
$env:LANGFUSE_PUBLIC_KEY = "your-public-key"
$env:LANGFUSE_BASE_URL = "https://cloud.langfuse.com"
python -m agents.production.pocs.observability.langfuse.main "What is an LLM gateway?"
```

The callback can capture prompt and completion content. Apply your data-handling, access-control, and retention requirements before using real user inputs.
