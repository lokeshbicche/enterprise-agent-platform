"""Demonstrate Deep Agents delegation to isolated specialist subagents."""

import os
import sys

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.orchestration.deep_agents.main "Your question"'
        )

    model = init_chat_model(
        os.environ.get("MODEL_NAME", "openai:gpt-4o-mini"),
        temperature=0,
        max_tokens=2_000,
    )
    agent = create_deep_agent(
        model=model,
        tools=[],
        subagents=[
            {
                "name": "benefits",
                "description": "Analyze benefits and strengths of the proposed options.",
                "system_prompt": (
                    "Analyze only the task provided. Return a concise list of "
                    "potential benefits and state any assumptions."
                ),
                "tools": [],
            },
            {
                "name": "risks",
                "description": "Analyze risks, tradeoffs, and operational concerns.",
                "system_prompt": (
                    "Analyze only the task provided. Return a concise list of "
                    "risks and tradeoffs; do not invent external facts."
                ),
                "tools": [],
            },
        ],
        system_prompt=(
            "You are a synthesis agent. Delegate independent analysis to the "
            "benefits and risks subagents, then combine their results into a "
            "balanced response. Do not claim external research was performed."
        ),
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 12},
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
