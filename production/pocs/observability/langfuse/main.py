"""Trace a LangChain agent with the Langfuse callback handler."""

import os
import sys

from langchain.agents import create_agent
from langfuse import get_client
from langfuse.langchain import CallbackHandler


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.observability.langfuse.main "Your question"'
        )
    required = ("OPENAI_API_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_PUBLIC_KEY")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit(f"Set required environment variables: {', '.join(missing)}")

    client = get_client()
    handler = CallbackHandler()
    agent = create_agent(
        model=os.environ.get("MODEL_NAME", "openai:gpt-4o-mini"),
        tools=[],
        system_prompt="Answer briefly. State uncertainty rather than inventing facts.",
    )
    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"callbacks": [handler]},
        )
    finally:
        client.flush()
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
