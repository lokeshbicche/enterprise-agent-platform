# OpenRouter Gateway POC

Calls OpenRouter through its OpenAI-compatible API. OpenRouter supports many model providers behind one endpoint; model availability, routing, privacy, and pricing depend on the chosen model and account settings.

## Run

```powershell
python -m venv .venv-openrouter
.\.venv-openrouter\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\model_gateways\openrouter\requirements.txt
$env:OPENROUTER_API_KEY = "your-openrouter-key"
$env:OPENROUTER_MODEL = "openai/gpt-4o-mini"
python -m agents.production.pocs.model_gateways.openrouter.main "Say hello in one sentence."
```

Choose a model slug available to your account. Review provider routing and data-handling options before sending sensitive data.
