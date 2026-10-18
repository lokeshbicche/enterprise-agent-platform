# LiteLLM Proxy POC

The YAML config defines a stable `enterprise-chat` alias, a primary OpenAI model, an Anthropic fallback, and an environment-provided proxy master key. LiteLLM's proxy is an OpenAI-compatible gateway; the client does not need provider-specific logic.

## Start the proxy

Use a dedicated environment and install the proxy distribution:

```powershell
python -m venv .venv-litellm
.\.venv-litellm\Scripts\Activate.ps1
python -m pip install -r agents\production\pocs\model_gateways\litellm_proxy\requirements.txt
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"
$env:LITELLM_MASTER_KEY = "a-long-random-proxy-key"
litellm --config agents\production\pocs\model_gateways\litellm_proxy\config.yaml
```

In another terminal using that environment, provide the proxy key and call the alias:

```powershell
$env:LITELLM_BASE_URL = "http://localhost:4000/v1"
$env:LITELLM_API_KEY = "the-same-local-LITELLM_MASTER_KEY"
python -m agents.production.pocs.model_gateways.litellm_proxy.main "Say hello in one sentence."
```

Keep the proxy private, use TLS and a secrets manager outside local development, configure authentication/rate/cost policies, and pin the proxy image/package version in a real deployment.
