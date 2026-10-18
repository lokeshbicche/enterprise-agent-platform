# enterprise-agent-platform

A basic AI agent written in **plain Python** (standard library only, no AI frameworks) to understand how an agent works.

## The agent loop

```
PERCEIVE -> THINK -> ACT -> OBSERVE -> REMEMBER -> RESPOND
```

| Step     | Method in `python_basic_agent_without_AI.py` | What it does                                            |
|----------|----------------------------|---------------------------------------------------------|
| Perceive | `BasicAgent.perceive()`    | Receives the user goal and stores it in memory          |
| Think    | `BasicAgent.think()`       | Splits the goal into sub-tasks and picks a tool for each |
| Act      | `BasicAgent.act()`         | Runs the chosen tool                                    |
| Observe  | `BasicAgent.observe()`     | Records the tool result in memory                       |
| Respond  | `BasicAgent.respond()`     | Combines results into the final answer                  |

Tools: `calculator`, `time`, `word_count`, `reverse`, `remember`, `recall`, `help`.
In a production agent the `think()` step would call an LLM; here it is rule-based so the flow is easy to follow.

## Run (Python 3.8+)

```bash
python python_basic_agent_without_AI.py           # interactive chat
python python_basic_agent_without_AI.py --demo    # scripted demo
python -m unittest -v           # tests
```

Example prompts: `calculate (12 + 8) * 3`, `remember my name is Bicche`, `what is my name`,
`what time is it and then calculate 2 ^ 10`, `count words in cats and dogs`, `reverse hello`.

## Extend it

```python
from python_basic_agent_without_AI import BasicAgent, Tool

agent = BasicAgent()
agent.register_tool(Tool("upper", "Uppercase text", lambda text: text.upper()))
```
Then add a rule for it in `BasicAgent._choose_tool()`.

## With AI: raw HTTP vs SDK

Same agent, same tools — **only the THINK step changes**: the goal and tool list are sent to an LLM,
which returns the plan as JSON. Two versions, identical except for `call_llm()`:

| File | How it calls the LLM | Install |
|------|----------------------|---------|
| `python_basic_agent_with_AI_rawhttp.py` | Raw HTTP with built-in `urllib` (you build URL, headers, JSON) | nothing |
| `python_basic_agent_with_AI_sdk.py` | Official OpenAI SDK (`client.chat.completions.create`) | `pip install openai` |

Compare any two files in VS Code: select both → right-click → *Compare Selected*.

```powershell
# OpenAI (cloud, needs key)
$env:LLM_API_KEY="sk-..."                                   # optional: $env:LLM_MODEL (default gpt-4o-mini)
# or Ollama (local, free, no key)
$env:LLM_BASE_URL="http://localhost:11434/v1"; $env:LLM_MODEL="llama3.2"

python python_basic_agent_with_AI_rawhttp.py --demo
python python_basic_agent_with_AI_sdk.py --demo
```
Without a key/server (or without the SDK installed) both fall back to the rule-based planner, so they always run.

## Model SDKs: one file per provider (`python_basic_agent_modelsdk_*.py`)

A **model SDK** only replaces the LLM call. Each file is the same `BasicAgent` (same tools, same loop, same demo);
the THINK step calls one provider class, e.g. `AnthropicModelSDK.call(system_prompt, user_prompt)`.
Compare two of these files to see how providers differ.

| File | Class | Install | Configure (env vars) |
|------|-------|---------|----------------------|
| `python_basic_agent_modelsdk_openai.py` | `OpenAIModelSDK` | `pip install openai` | `OPENAI_API_KEY` |
| `python_basic_agent_modelsdk_anthropic.py` | `AnthropicModelSDK` | `pip install anthropic` | `ANTHROPIC_API_KEY` |
| `python_basic_agent_modelsdk_google_genai.py` | `GoogleGenAIModelSDK` | `pip install google-genai` | `GEMINI_API_KEY` (free tier) |
| `python_basic_agent_modelsdk_azure_openai.py` | `AzureOpenAIModelSDK` | `pip install openai` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT` |
| `python_basic_agent_modelsdk_aws_bedrock.py` | `AWSBedrockModelSDK` | `pip install boto3` | AWS credentials (`aws configure`), `AWS_REGION` |
| `python_basic_agent_modelsdk_mistral.py` | `MistralModelSDK` | `pip install mistralai` | `MISTRAL_API_KEY` |
| `python_basic_agent_modelsdk_cohere.py` | `CohereModelSDK` | `pip install cohere` | `COHERE_API_KEY` |
| `python_basic_agent_modelsdk_groq.py` | `GroqModelSDK` | `pip install groq` | `GROQ_API_KEY` (free tier) |
| `python_basic_agent_modelsdk_ollama.py` | `OllamaModelSDK` | `pip install ollama` | none - local Ollama app, `OLLAMA_MODEL` |
| `python_basic_agent_modelsdk_huggingface.py` | `HuggingFaceModelSDK` | `pip install huggingface_hub` | `HF_TOKEN` |
| `python_basic_agent_modelsdk_litellm.py` | `LiteLLMModelSDK` | `pip install litellm` | `LITELLM_MODEL` (e.g. `ollama/llama3.2`) + that provider's key |

## Agent SDKs: one file per framework (`python_basic_agent_agentsdk_*.py`)

An **agent SDK** replaces the whole `BasicAgent` loop: you give it a model, instructions and plain Python
functions as tools, and it does THINK -> ACT -> OBSERVE (tool calling) and memory for you.
All files share the same tools and demo; only the `...Agent` class is framework-specific.

| File | Class | Install |
|------|-------|---------|
| `python_basic_agent_agentsdk_openai_agents.py` | `OpenAIAgentsSDKAgent` | `pip install openai-agents` |
| `python_basic_agent_agentsdk_google_adk.py` | `GoogleADKAgent` | `pip install google-adk litellm mcp` |
| `python_basic_agent_agentsdk_claude_agent.py` | `ClaudeAgentSDKAgent` | `pip install claude-agent-sdk` |
| `python_basic_agent_agentsdk_semantic_kernel.py` | `SemanticKernelAgent` | `pip install semantic-kernel` |
| `python_basic_agent_agentsdk_autogen.py` | `AutoGenAgent` | `pip install autogen-agentchat "autogen-ext[openai]"` |
| `python_basic_agent_agentsdk_microsoft_agent_framework.py` | `MicrosoftAgentFrameworkAgent` | `pip install agent-framework` |
| `python_basic_agent_agentsdk_strands.py` | `StrandsAgent` | `pip install "strands-agents[openai]"` |
| `python_basic_agent_agentsdk_langgraph.py` | `LangGraphAgent` | `pip install langchain langgraph langchain-openai` |
| `python_basic_agent_agentsdk_crewai.py` | `CrewAIAgent` | `pip install crewai` |
| `python_basic_agent_agentsdk_llamaindex.py` | `LlamaIndexAgent` | `pip install llama-index-core llama-index-llms-openai-like` |
| `python_basic_agent_agentsdk_smolagents.py` | `SmolAgentsAgent` | `pip install "smolagents[openai]"` |
| `python_basic_agent_agentsdk_pydantic_ai.py` | `PydanticAIAgent` | `pip install "pydantic-ai-slim[openai]"` |

Configure with `OPENAI_API_KEY` (or `OPENAI_BASE_URL=http://localhost:11434/v1` + `OPENAI_MODEL=llama3.2` for free local Ollama).
Exceptions: Claude Agent SDK needs `ANTHROPIC_API_KEY`; Google ADK uses `GOOGLE_API_KEY` (Gemini) if set.

Tip: frameworks have conflicting dependencies - use one virtual environment per SDK:
```powershell
python -m venv .venv-langgraph; .venv-langgraph\Scripts\activate; pip install langchain langgraph langchain-openai
python python_basic_agent_agentsdk_langgraph.py --demo
```
Every `modelsdk` / `agentsdk` file runs the rule-based agent instead if its package or key is missing, so it never crashes.

## Model SDK vs agent SDK in production

An agent SDK always calls a model SDK underneath. The real choice is **who writes the agent loop**.

| | Model SDK + your own loop | Agent SDK |
|---|---|---|
| Good for | Clear, fixed jobs: support bots, document Q&A, extraction | Many steps/tools, multi-agent, long-running, human approval |
| Pros | Full control, easy to debug, few dependencies, predictable cost | State, handoffs, tracing, MCP, streaming built in; faster to ship |
| Cons | You build retries, memory, tracing, guardrails yourself | Hidden behaviour, more dependencies, APIs change often |

Rule of thumb: start with a model SDK + the model's built-in tool calling; move to an agent SDK when you are
rebuilding state, retries, handoffs or tracing by hand. Either way, production also needs guardrails, logging/tracing,
evaluation tests, rate/cost limits, secrets management, and timeouts with fallbacks.

## Which model SDK each agent SDK uses underneath

| Agent SDK | Default model call | LiteLLM? |
|---|---|---|
| OpenAI Agents SDK | `openai` | optional (`LitellmModel`) |
| Google ADK | `google-genai` (Gemini) | for non-Gemini models (`LiteLlm`) |
| Claude Agent SDK | Claude Code CLI -> Anthropic API | no |
| Semantic Kernel | `openai` (+ own connectors) | no |
| AutoGen | `openai` (`OpenAIChatCompletionClient`) | no |
| Microsoft Agent Framework | `openai` | no |
| AWS Strands | `boto3` (Bedrock); these files use its `openai` provider | optional |
| LangChain / LangGraph | `langchain-openai` (wraps `openai`) | optional |
| CrewAI | its `LLM` class (direct for main providers in newer versions) | yes, at least as fallback |
| LlamaIndex | `openai` (`OpenAILike`) | optional |
| smolagents | `openai` (`OpenAIModel`) | optional (`LiteLLMModel`) |
| Pydantic AI | `openai` | no |

The `openai` SDK is the most common because many providers and local servers (Ollama, Groq, vLLM, Azure) copy its API format.
In each `python_basic_agent_agentsdk_*.py` class you can see the model-SDK object (`AsyncOpenAI`, `ChatOpenAI`, `LiteLlm`...)
that actually calls the LLM; the agent SDK runs the loop around it.

## LiteLLM and other ways to connect multiple providers

**LiteLLM** works at the model layer only (no agent loop, planning or memory). Two forms:
- **Python SDK**: `litellm.completion(model="anthropic/claude-haiku-4-5", ...)` - one function for 100+ providers
  (see `python_basic_agent_modelsdk_litellm.py`).
- **Proxy server (AI gateway)**: apps call it in OpenAI format; it adds per-team keys, budgets, rate limits, fallbacks,
  load balancing, caching, logging and cost tracking. This is how it is mostly used in production (open source + paid Enterprise).

Enterprise options for many providers:

| Option | Examples | Why |
|---|---|---|
| Cloud model platform | AWS Bedrock, Azure AI Foundry, Google Vertex AI (Model Garden) | Data stays in your cloud, existing billing, IAM and compliance |
| AI gateway | LiteLLM Proxy, Portkey, TrueFoundry, Helicone, Azure API Management, Kong AI Gateway, Cloudflare AI Gateway, Envoy AI Gateway, Databricks Mosaic AI Gateway | One company-wide entry point: keys, budgets, fallbacks, logging, guardrails |
| Hosted aggregator | OpenRouter | One key for hundreds of models; good for prototypes, less common in enterprises |
| Library in your code | LiteLLM SDK, LangChain chat models, Semantic Kernel connectors, Spring AI (Java), Vercel AI SDK (JS/TS) | No extra server |
| Your own adapter layer | One interface + a class per provider (like the `...ModelSDK` classes here) | Full control, often with a gateway behind it |

Common enterprise setup:
```
apps / agents -> AI gateway (LiteLLM Proxy, Kong, Azure APIM, Portkey...)
              -> Bedrock / Azure / Vertex / OpenAI / Anthropic / self-hosted (vLLM, Ollama)
```
