"""Run a small LangChain agent that LangSmith traces from environment settings."""

import os
import sys

from langchain.agents import create_agent


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.observability.langsmith.main "Your question"'
        )
    if os.environ.get("LANGSMITH_TRACING", "").lower() != "true":
        raise SystemExit("Set LANGSMITH_TRACING=true to enable the tracing POC.")

    agent = create_agent(
        model=os.environ.get("MODEL_NAME", "openai:gpt-4o-mini"),
        tools=[],
        system_prompt="Answer briefly. State uncertainty rather than inventing facts.",
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
