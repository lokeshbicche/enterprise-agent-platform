"""Focused tests for production API request validation."""

import unittest
from uuid import UUID

from pydantic import ValidationError

from agents.production.config import Settings
from agents.production.schemas import AgentRequest


class AgentRequestTests(unittest.TestCase):
    def test_question_is_trimmed_and_thread_id_is_generated(self) -> None:
        request = AgentRequest(question="  Help me design an API.  ")

        self.assertEqual(request.question, "Help me design an API.")
        self.assertIsInstance(request.thread_id, UUID)

    def test_blank_question_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            AgentRequest(question=" \t ")

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            AgentRequest.model_validate({"question": "hello", "admin": True})

    def test_question_length_is_bounded(self) -> None:
        with self.assertRaises(ValidationError):
            AgentRequest(question="x" * 8_001)

    def test_settings_reject_short_bearer_token(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(
                postgres_dsn="postgresql://localhost/agent_platform",
                openai_api_key="test-key",
                api_bearer_token="short",
            )

    def test_settings_reject_invalid_pool_bounds(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(
                postgres_dsn="postgresql://localhost/agent_platform",
                openai_api_key="test-key",
                api_bearer_token="a" * 32,
                postgres_pool_min_size=5,
                postgres_pool_max_size=2,
            )


if __name__ == "__main__":
    unittest.main()
