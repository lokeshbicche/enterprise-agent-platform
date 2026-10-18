# Agent With HTTP

This example keeps the basic agent loop and calls an OpenAI-compatible chat endpoint using Python's built-in `urllib`; no model-provider SDK is required. If the model is not configured or the request fails, it falls back to the rule-based planner.

See [the implementation](python_basic_agent_with_AI_rawhttp.py) for details.

## Run

Run commands from the repository root:

```powershell
python -m agents.with_http.python_basic_agent_with_AI_rawhttp
python -m agents.with_http.python_basic_agent_with_AI_rawhttp --demo
```

For a cloud endpoint, configure the API key and optionally choose a model:

```powershell
$env:LLM_API_KEY="your-key"
$env:LLM_MODEL="gpt-4o-mini"
```

For local Ollama, start its server and configure the compatible endpoint; no provider API key is needed:

```powershell
$env:LLM_BASE_URL="http://localhost:11434/v1"
$env:LLM_MODEL="llama3.2"
```
