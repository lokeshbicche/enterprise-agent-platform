"""Run the bounded planner -> specialist -> reviewer graph."""

import asyncio
import os
import sys
from uuid import uuid4

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agents.production.workflows import (
    WorkflowState,
    build_multi_agent_graph,
    make_thread_config,
)


async def run(question: str) -> str:
    model = init_chat_model(
        os.environ.get("MODEL_NAME", "openai:gpt-4o-mini"),
        temperature=0,
        max_tokens=2_000,
    )
    graph = build_multi_agent_graph(model, InMemorySaver())
    state: WorkflowState = {
        "question": question,
        "plan": "",
        "draft": "",
        "answer": "",
        "messages": [HumanMessage(content=question)],
    }
    result = await graph.ainvoke(
        state,
        config=make_thread_config(
            thread_id=uuid4(),
            principal="local-poc",
            workflow="multi-agent",
        ),
    )
    return result["answer"]


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit(
            'Usage: python -m agents.production.pocs.orchestration.multi_agent.main "Your question"'
        )
    print(asyncio.run(run(question)))


if __name__ == "__main__":
    main()
