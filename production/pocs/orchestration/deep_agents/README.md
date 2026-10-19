# Deep Agents POC

Uses Deep Agents' delegated `task` capability with two isolated, read-only subagents. The subagents receive a research task but have no tools or external data access; this keeps the demo safe and does not imply web research.

## Run

```powershell
python -m venv .venv-deep-agent
.\.venv-deep-agent\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\orchestration\deep_agents\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
$env:MODEL_NAME = "openai:gpt-4o-mini"
python -m agents.production.pocs.orchestration.deep_agents.main "Compare blue/green and rolling deployments."
```

Set the credential environment variable required by the provider in `MODEL_NAME`. The SDK exposes filesystem and planning capabilities; this POC intentionally gives it no external business tools.
