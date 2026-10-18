# Enterprise Agent Platform

Learning examples for building agents, from a rule-based loop to LLM-powered agent frameworks. Run examples from the repository root with `python -m`.

## Guides

- [Agent without AI](agents/without_ai/README.md): rule-based planning, tools, memory, and tests.
- [Agent with HTTP](agents/with_http/README.md): call an OpenAI-compatible model endpoint using standard-library HTTP.
- [Agent with model SDK](agents/with_model_sdk/README.md): use provider SDKs while keeping the basic agent loop.
- [Agent with agent SDK](agents/with_agent_sdk/README.md): use frameworks that manage the agent loop and tool calls.
- [Agent with MCP](agents/with_mcp/README.md): discover and call tools exposed by an MCP server.
- [Agent with RAG](agents/rag/README.md): retrieve relevant in-memory policy passages and answer from that evidence.
- [Production RAG learning path](agents/rag/production/README.md): seven-stage pipeline, separate Chroma/Pinecone/Weaviate POCs, advanced retrieval, evaluation, use cases, and POC-to-enterprise guidance.
- [Agent with vector search](agents/vector/README.md): rank an in-memory product catalog and compare vector cache, persistence, and tiered storage POCs.
- [Agent with LangChain](agents/with_langchain/README.md): use LangChain to run a model with a read-only tool.
- [Production agent API](agents/production/README.md): authenticated FastAPI, Pydantic, LangGraph multi-agent workflows, Deep Agents, and PostgreSQL checkpoints.
- [Production agent POCs](agents/production/pocs/README.md): categorized orchestration, gateway, and observability proofs of concept.
- [Production agent capabilities](agents/production/capabilities/README.md): evaluation, safety, memory, observability, cost, application, infrastructure, prompt, and dataset POCs.

Install only the dependencies for the example you want to run. SDK dependencies may conflict, so use separate virtual environments when comparing frameworks. Each guide has setup and run instructions for its folder.

MCP is a protocol for connecting tools, RAG is a retrieval-and-answering pattern, vector search is one retrieval technique, and LangChain is an agent framework. They can also be combined; these small examples isolate each concept. The original learning examples use in-memory sample data; the production guide separately demonstrates PostgreSQL-backed workflow checkpoints.

## Quick start

```powershell
# No model or API key required
python -m agents.without_ai.python_basic_agent_without_AI --demo

# Run the no-AI tests
python -m unittest discover -s agents/without_ai -v
```
