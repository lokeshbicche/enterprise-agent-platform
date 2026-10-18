"""Offline integration tests for the Chroma and Qdrant POCs."""

from contextlib import redirect_stdout
from io import StringIO
import os
import tempfile
import unittest
from unittest.mock import patch

from qdrant_client import QdrantClient

from agents.vector.cache import main as cache_poc
from agents.vector.database import main as database_poc
from agents.vector.tiered import main as tiered_poc


def fake_embedding(text: str) -> list[float]:
    normalized = text.lower()
    if "chair" in normalized:
        return [0.0, 1.0, 0.0]
    if "headphone" in normalized:
        return [0.0, 0.0, 1.0]
    if "dock" in normalized or "monitor" in normalized:
        return [0.7, 0.0, 0.7]
    return [1.0, 0.0, 0.0]


class VectorPocTests(unittest.TestCase):
    def test_ephemeral_chroma_cache_returns_semantic_match(self) -> None:
        output = StringIO()
        with (
            patch.object(cache_poc, "embed_text", side_effect=fake_embedding),
            patch("sys.argv", ["main", "--demo"]),
            redirect_stdout(output),
        ):
            cache_poc.main()

        self.assertIn("Vector-store cache", output.getvalue())
        self.assertIn("Travel laptop", output.getvalue())

    def test_qdrant_database_persists_and_returns_match(self) -> None:
        with tempfile.TemporaryDirectory() as storage_path:
            output = StringIO()
            with (
                patch.dict(os.environ, {"QDRANT_PATH": storage_path}),
                patch.object(
                    database_poc,
                    "embed_texts",
                    side_effect=lambda texts: [fake_embedding(text) for text in texts],
                ),
                patch.object(database_poc, "embed_text", side_effect=fake_embedding),
                patch("sys.argv", ["main", "--demo"]),
                redirect_stdout(output),
            ):
                database_poc.main()

            self.assertIn("Persistent Qdrant database", output.getvalue())
            self.assertIn("Ergonomic office chair", output.getvalue())

            client = QdrantClient(path=storage_path)
            try:
                count = client.count(
                    collection_name=database_poc.COLLECTION,
                    exact=True,
                ).count
            finally:
                client.close()
            self.assertEqual(count, 4)

    def test_tiered_poc_promotes_database_result_into_hot_cache(self) -> None:
        with tempfile.TemporaryDirectory() as storage_path:
            output = StringIO()
            embed_catalog = patch.object(
                tiered_poc,
                "embed_texts",
                side_effect=lambda texts: [fake_embedding(text) for text in texts],
            )
            with (
                patch.dict(os.environ, {"QDRANT_PATH": storage_path}),
                embed_catalog as embed_catalog_mock,
                patch.object(tiered_poc, "embed_text", side_effect=fake_embedding),
                patch("sys.argv", ["main", "--demo"]),
                redirect_stdout(output),
            ):
                tiered_poc.main()
                tiered_poc.main()

            result = output.getvalue()
            self.assertEqual(result.count("CACHE MISS -> DATABASE"), 2)
            self.assertEqual(result.count("CACHE HIT"), 2)
            self.assertIn("Travel laptop", result)
            embed_catalog_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
