# LangSmith Tracing POC

LangSmith tracing records LangChain agent runs, model calls, and tool interactions. This example opts in using environment variables; no LangSmith SDK call is needed in the application code.

## Run

```powershell
python -m venv .venv-langsmith-tracing
.\.venv-langsmith-tracing\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\observability\langsmith\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
$env:LANGSMITH_TRACING = "true"
$env:LANGSMITH_API_KEY = "your-langsmith-key"
$env:LANGSMITH_PROJECT = "agent-platform-poc"
python -m agents.production.pocs.observability.langsmith.main "What is an LLM gateway?"
```

Use `LANGSMITH_ENDPOINT` for non-default regions. Traces can include prompts and model outputs: configure redaction, project access, and retention appropriately.
