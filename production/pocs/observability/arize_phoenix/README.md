# Arize Phoenix Tracing POC

Starts Phoenix locally in Docker and instruments a LangChain chain using OpenInference and OpenTelemetry. It exports traces to a local OTLP collector and does not require a Phoenix API key.

## Start Phoenix

```powershell
docker run --rm -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest
```

Open the Phoenix UI at `http://localhost:6006`. For shared or production environments, pin an approved Phoenix image version and configure persistent storage and access control.

## Run the instrumented chain

In another terminal:

```powershell
python -m venv .venv-phoenix
.\.venv-phoenix\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\observability\arize_phoenix\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.production.pocs.observability.arize_phoenix.main "What is an LLM gateway?"
```

For a remote collector, set `PHOENIX_COLLECTOR_ENDPOINT` to its OTLP HTTP traces URL, such as `https://phoenix.example.com/v1/traces`.
