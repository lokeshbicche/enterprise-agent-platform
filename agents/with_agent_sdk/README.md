# Agent With Agent SDK

These examples use frameworks that manage the agent loop and tool calling. Each implementation uses the same basic tasks but a different agent framework. Install only the framework dependencies for the example you plan to run; dependency sets can conflict, so separate virtual environments are recommended.

Run commands from the repository root with `python -m`. Each source file documents its package, credentials, and fallback behavior.

## Examples

- [AutoGen](python_basic_agent_agentsdk_autogen.py)
- [Claude Agent SDK](python_basic_agent_agentsdk_claude_agent.py)
- [CrewAI](python_basic_agent_agentsdk_crewai.py)
- [Google ADK](python_basic_agent_agentsdk_google_adk.py)
- [LangGraph](python_basic_agent_agentsdk_langgraph.py)
- [LlamaIndex](python_basic_agent_agentsdk_llamaindex.py)
- [Microsoft Agent Framework](python_basic_agent_agentsdk_microsoft_agent_framework.py)
- [OpenAI Agents SDK](python_basic_agent_agentsdk_openai_agents.py)
- [Pydantic AI](python_basic_agent_agentsdk_pydantic_ai.py)
- [Semantic Kernel](python_basic_agent_agentsdk_semantic_kernel.py)
- [smolagents](python_basic_agent_agentsdk_smolagents.py)
- [Strands](python_basic_agent_agentsdk_strands.py)

## Run LangGraph

For example, create an environment with LangGraph dependencies, configure a model, then run from the repository root:

```powershell
python -m pip install langchain langgraph langchain-openai
$env:OPENAI_API_KEY="your-key"
python -m agents.with_agent_sdk.python_basic_agent_agentsdk_langgraph --demo
```
