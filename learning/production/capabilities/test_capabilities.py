"""Offline tests for the production capability examples."""

import unittest

from agents.production.capabilities.context_memory.main import (
    add_message,
    build_context,
    create_store,
    remember_fact,
)
from agents.production.capabilities.cost_performance.main import (
    ModelRate,
    TTLCache,
    estimate_cost,
)
from agents.production.capabilities.datasets_input_output.main import (
    DATASET_PATH,
    load_dataset,
    parse_record,
)
from agents.production.capabilities.evaluation_at_scale.main import run_batch
from agents.production.capabilities.evaluation_quality.main import (
    EvaluationCase,
    evaluate,
    run_evaluation,
)
from agents.production.capabilities.guardrails_safety.main import (
    authorize_tool,
    inspect_output,
    validate_request,
)
from agents.production.capabilities.observability_monitoring.main import (
    RequestMetrics,
    redact,
)
from agents.production.capabilities.prompt_engineering.main import PROMPT, validate_prompt
from agents.production.capabilities.user_experience_application.main import (
    ChatRequest,
    app,
)
from fastapi.testclient import TestClient


class EvaluationTests(unittest.TestCase):
    def test_quality_demo_has_expected_pass_rate(self) -> None:
        result = run_evaluation()
        self.assertEqual(result["total"], 3)
        self.assertEqual(result["pass_rate"], 1.0)

    def test_exact_match_fails_when_only_required_term_matches(self) -> None:
        case = EvaluationCase(
            case_id="capital-wrong",
            expected="Canberra is the capital of Australia.",
            required_terms=("Canberra",),
            actual="Canberra is the capital of Austria.",
        )
        result = evaluate(case)
        self.assertFalse(result["passed"])
        self.assertFalse(result["exact_match"])

    def test_scaled_evaluation_completes_all_cases(self) -> None:
        result = run_batch(max_workers=2)
        self.assertEqual(result["passed"], result["total"])


class GuardrailTests(unittest.TestCase):
    def test_request_and_tool_allowlist(self) -> None:
        self.assertFalse(validate_request("  ").allowed)
        self.assertFalse(validate_request("x" * 2_001).allowed)
        self.assertTrue(authorize_tool("faq_lookup").allowed)
        self.assertFalse(authorize_tool("execute_shell").allowed)

    def test_output_secret_pattern_is_redacted_and_blocked(self) -> None:
        result = inspect_output("fake key sk-demoCredential123456")
        self.assertFalse(result.allowed)
        self.assertNotIn("sk-demoCredential123456", result.sanitized_output or "")


class MemoryTests(unittest.TestCase):
    def test_memory_is_session_scoped_and_history_bounded(self) -> None:
        with create_store() as connection:
            remember_fact(connection, "session-a", "language", "English")
            add_message(connection, "session-a", 1, "user", "first")
            add_message(connection, "session-a", 2, "user", "second")
            add_message(connection, "session-a", 3, "assistant", "third")
            add_message(connection, "session-a", 4, "user", "fourth")
            context = build_context(connection, "session-a")
            other_session = build_context(connection, "session-b")

        self.assertIn("language=English", context)
        self.assertNotIn("first", context)
        self.assertEqual(other_session, "")


class CostAndObservabilityTests(unittest.TestCase):
    def test_cost_estimator_and_cache_expiration(self) -> None:
        self.assertAlmostEqual(
            estimate_cost(1_000, 250, ModelRate(0.15, 0.60)),
            0.0003,
        )
        now = [0.0]
        cache = TTLCache(ttl_seconds=5, clock=lambda: now[0])
        cache.set("query", "answer")
        self.assertEqual(cache.get("query"), "answer")
        now[0] = 5.0
        self.assertIsNone(cache.get("query"))

    def test_redaction_and_metrics(self) -> None:
        self.assertNotIn("sk-testSecret12345", redact("key sk-testSecret12345"))
        metrics = RequestMetrics()
        metrics.observe("ok", 2.0)
        metrics.observe("error", 4.0)
        self.assertEqual(metrics.summary()["errors_total"], 1)


class PromptAndDatasetTests(unittest.TestCase):
    def test_prompt_template_has_required_sections(self) -> None:
        rendered = PROMPT.render("question", "reference")
        self.assertEqual(validate_prompt(rendered), [])

    def test_dataset_has_unique_ids_and_rejects_invalid_records(self) -> None:
        records = load_dataset(DATASET_PATH)
        self.assertEqual(len(records), 3)
        self.assertEqual(len({record.record_id for record in records}), 3)
        with self.assertRaises(ValueError):
            parse_record({"record_id": "bad"}, 1)


class ApplicationLayerTests(unittest.TestCase):
    def test_chat_endpoint_and_request_validation(self) -> None:
        client = TestClient(app)
        response = client.post("/v1/chat", json={"message": "hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "POC received: hello")
        self.assertEqual(
            client.post("/v1/chat", json={"message": "  "}).status_code,
            422,
        )
        self.assertEqual(
            client.post(
                "/v1/chat",
                json={"message": "hello", "admin": True},
            ).status_code,
            422,
        )

    def test_chat_schema_rejects_oversized_request(self) -> None:
        with self.assertRaises(ValueError):
            ChatRequest(message="x" * 4_001)


if __name__ == "__main__":
    unittest.main()
