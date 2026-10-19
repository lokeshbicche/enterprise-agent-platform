"""Tests for bounded workflow orchestration without a model API or database."""

import unittest
from uuid import UUID

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agents.production.workflows import (
    WorkflowState,
    build_deep_agent_graph,
    build_multi_agent_graph,
    make_thread_config,
)


class ToolAwareFakeChatModel(FakeListChatModel):
    def bind_tools(self, tools: object, **kwargs: object) -> "ToolAwareFakeChatModel":
        return self


class MultiAgentWorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_planner_specialist_reviewer_pipeline(self) -> None:
        model = FakeListChatModel(responses=["plan", "draft", "reviewed answer"])
        graph = build_multi_agent_graph(model, InMemorySaver())
        state: WorkflowState = {
            "question": "Explain an API gateway.",
            "plan": "",
            "draft": "",
            "answer": "",
            "messages": [HumanMessage(content="Explain an API gateway.")],
        }

        result = await graph.ainvoke(
            state,
            config=make_thread_config(
                UUID(int=1),
                "test-principal",
                "multi-agent",
            ),
        )

        self.assertEqual(result["answer"], "reviewed answer")
        self.assertEqual(len(result["messages"]), 2)
        self.assertEqual(result["messages"][-1].content, "reviewed answer")

    async def test_deep_agent_workflow_returns_and_checkpoints_answer(self) -> None:
        graph = build_deep_agent_graph(
            ToolAwareFakeChatModel(responses=["deep answer"]),
            InMemorySaver(),
        )
        state: WorkflowState = {
            "question": "Explain an API gateway.",
            "plan": "",
            "draft": "",
            "answer": "",
            "messages": [HumanMessage(content="Explain an API gateway.")],
        }

        result = await graph.ainvoke(
            state,
            config=make_thread_config(
                UUID(int=2),
                "test-principal",
                "deep-agent",
            ),
        )

        self.assertEqual(result["answer"], "deep answer")
        self.assertEqual(result["messages"][-1].content, "deep answer")

    def test_thread_ids_are_scoped_to_principal_and_workflow(self) -> None:
        thread_id = UUID(int=1)
        multi_agent = make_thread_config(thread_id, "principal", "multi-agent")
        deep_agent = make_thread_config(thread_id, "principal", "deep-agent")

        self.assertNotEqual(
            multi_agent["configurable"]["thread_id"],
            deep_agent["configurable"]["thread_id"],
        )
        self.assertEqual(multi_agent["recursion_limit"], 10)


if __name__ == "__main__":
    unittest.main()
