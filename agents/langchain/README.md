# Agent With LangChain

This example uses a LangChain agent with one read-only tool to answer questions about sample order delivery. The sample order data lives in process memory only; no conversation checkpoint or persistent store is configured.

## Install and run

From the repository root, install the LangChain packages and set a model-provider key:

```powershell
python -m pip install langchain langchain-openai
$env:OPENAI_API_KEY="your-key"
python -m agents.with_langchain.agent_langchain_order_lookup --demo
```

The `--demo` request asks about `ORD-100`. You can also run without `--demo` and ask about `ORD-100` or `ORD-200`. The model call requires an OpenAI API key; the example's order lookup itself is in-memory and read-only.
