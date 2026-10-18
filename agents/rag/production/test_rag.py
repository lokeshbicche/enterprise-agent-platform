"""Offline tests for the production RAG learning examples."""

import unittest

from agents.rag.production.advanced.main import (
    compress_results,
    evaluate_retrieval,
    multi_query_retrieve,
    route_query,
)
from agents.rag.production.pipeline.main import (
    Chunk,
    SourceDocument,
    augment_context,
    chunk_documents,
    generate_answer,
    retrieve,
    run_pipeline,
)


class RagPipelineTests(unittest.TestCase):
    def test_sentence_chunking_preserves_source_and_overlaps_when_it_fits(self) -> None:
        documents = (
            SourceDocument(
                "sample",
                "v1",
                "Alpha beta. Gamma delta. Epsilon zeta.",
                "test",
            ),
        )
        chunks = chunk_documents(documents, max_words=5, overlap_sentences=1)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].document_id, "sample")
        self.assertEqual(chunks[0].text, "Alpha beta. Gamma delta.")
        self.assertEqual(chunks[1].text, "Gamma delta. Epsilon zeta.")

    def test_retrieval_respects_use_case_filter(self) -> None:
        chunks = chunk_documents()

        self.assertEqual(
            retrieve("travel expenses receipts", chunks, allowed_use_cases={"hr"}),
            [],
        )
        matches = retrieve(
            "travel expenses receipts",
            chunks,
            allowed_use_cases={"finance"},
        )
        self.assertEqual(matches[0][1].document_id, "travel-policy")

    def test_pipeline_returns_cited_answer_and_stages(self) -> None:
        result = run_pipeline("How many leave days do full-time employees receive?")

        self.assertEqual(len(result["stages"]), 7)
        self.assertIn("leave-policy", result["answer"])
        self.assertIn("20 paid leave days", result["answer"])
        self.assertIn("[leave-policy v2026-01 #leave-policy:0]", result["context"])

    def test_no_evidence_abstains(self) -> None:
        result = run_pipeline("What is the company policy on lunar travel?")

        self.assertEqual(result["retrieved"], [])
        self.assertIn("don't have enough information", result["answer"])

    def test_blank_query_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_pipeline("   ")

    def test_context_budget_is_enforced(self) -> None:
        chunk = Chunk("large:0", "large", "v1", "x" * 1_500, "test")

        self.assertEqual(augment_context([(1.0, chunk)]), "")

    def test_answer_abstains_if_retrieved_text_has_no_query_evidence(self) -> None:
        chunk = Chunk("source:0", "source", "v1", "Unrelated material.", "test")

        answer = generate_answer("question about vacation", [(1.0, chunk)])

        self.assertIn("don't have enough information", answer)


class AdvancedRetrievalTests(unittest.TestCase):
    def test_query_router_suggests_domain_filter(self) -> None:
        self.assertEqual(route_query("How do I claim travel expenses?"), {"finance"})
        self.assertEqual(route_query("How much vacation leave?"), {"hr"})
        self.assertIsNone(route_query("What is the company mission?"))

    def test_multi_query_finds_synonym_match_and_compresses_evidence(self) -> None:
        chunks = chunk_documents()
        results = multi_query_retrieve("How many vacation days?", chunks)

        self.assertEqual(results[0][1].document_id, "leave-policy")
        compressed = compress_results("vacation days", results)
        self.assertTrue(compressed)
        self.assertTrue(
            any(chunk.document_id == "leave-policy" for _, chunk in compressed)
        )

    def test_evaluation_reports_expected_retrieval_metrics(self) -> None:
        metrics = evaluate_retrieval(
            [
                ("How many paid leave days?", {"leave-policy"}),
                ("When are travel expenses due?", {"travel-policy"}),
            ],
            chunk_documents(),
        )

        self.assertEqual(metrics["mrr"], 1.0)
        self.assertGreater(metrics["recall@3"], 0.0)

    def test_evaluation_rejects_missing_expected_sources(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_retrieval([("question", set())], chunk_documents())


if __name__ == "__main__":
    unittest.main()
