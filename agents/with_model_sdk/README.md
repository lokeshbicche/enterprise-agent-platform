# Agent With Model SDK

These examples keep the basic agent loop and vary how the model is called. The OpenAI SDK example uses an OpenAI-compatible chat API; the provider-specific examples demonstrate individual model SDKs. This is different from an agent SDK, which manages the agent loop itself.

Run commands from the repository root with `python -m`. Each example documents its package and configuration in its source header.

## OpenAI-compatible SDK example

Install the OpenAI package and configure credentials:

```powershell
python -m pip install openai
$env:LLM_API_KEY="your-key"
python -m agents.with_model_sdk.python_basic_agent_with_AI_sdk --demo
```

For local Ollama, set `LLM_BASE_URL` to `http://localhost:11434/v1` and set `LLM_MODEL` to the model you have installed. With the SDK missing or no endpoint configured, this example falls back to rules.

## Provider examples

- [OpenAI](python_basic_agent_modelsdk_openai.py)
- [Anthropic](python_basic_agent_modelsdk_anthropic.py)
- [AWS Bedrock](python_basic_agent_modelsdk_aws_bedrock.py)
- [Azure OpenAI](python_basic_agent_modelsdk_azure_openai.py)
- [Cohere](python_basic_agent_modelsdk_cohere.py)
- [Google Gemini](python_basic_agent_modelsdk_google_genai.py)
- [Groq](python_basic_agent_modelsdk_groq.py)
- [Hugging Face](python_basic_agent_modelsdk_huggingface.py)
- [LiteLLM](python_basic_agent_modelsdk_litellm.py)
- [Mistral](python_basic_agent_modelsdk_mistral.py)
- [Ollama](python_basic_agent_modelsdk_ollama.py)

See also the [OpenAI-compatible basic agent](python_basic_agent_with_AI_sdk.py).
