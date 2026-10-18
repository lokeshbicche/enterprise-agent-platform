# Production Agent POCs

Small, separate proof-of-concept examples for orchestration, LLM gateways, and LLM observability. Run commands from the repository root. Each POC has its own README and `requirements.txt`; use a separate virtual environment for each to avoid dependency conflicts.

These examples make external model or telemetry calls when run. Set credentials in your shell or an untracked local `.env`; never put real keys in source control. Do not send confidential production data to a hosted provider without the required security and privacy review.

## Orchestration

- [Multi-agent graph](orchestration/multi_agent/README.md): fixed planner -> specialist -> reviewer LangGraph pipeline.
- [Deep Agents](orchestration/deep_agents/README.md): Deep Agent delegating independent analysis to isolated subagents.

## Model gateways

- [LiteLLM Proxy](model_gateways/litellm_proxy/README.md): self-hosted OpenAI-compatible gateway with an alias and provider fallback.
- [OpenRouter](model_gateways/openrouter/README.md): provider/model routing through its OpenAI-compatible endpoint.
- [LangSmith LLM Gateway](model_gateways/langsmith_gateway/README.md): managed gateway call through the OpenAI client.

## Observability

- [LangSmith tracing](observability/langsmith/README.md): trace a LangChain agent using LangSmith callback environment configuration.
- [Langfuse tracing](observability/langfuse/README.md): instrument a LangChain agent with the Langfuse callback handler.
- [Arize Phoenix](observability/arize_phoenix/README.md): auto-instrument a LangChain chain and export traces to Phoenix.

LangSmith appears in both categories for different purposes: the gateway routes model traffic, while LangSmith tracing records LangChain execution. Gateway POCs are alternatives; observability backends can be evaluated separately and should not all receive production prompts by default.
