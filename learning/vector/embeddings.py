"""Shared embedding helper for vector-store proof-of-concept examples."""

import os
from collections.abc import Sequence
from functools import lru_cache

from openai import OpenAI


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY before creating embeddings.")
    return OpenAI()


def embed_texts(texts: Sequence[str]) -> list[list[float]]:
    """Create embeddings in input order using one API request."""

    if not texts:
        return []
    client = _client()
    response = client.embeddings.create(
        model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
        input=list(texts),
    )
    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]


def embed_text(text: str) -> list[float]:
    """Create one semantic text embedding using the configured OpenAI API."""

    return embed_texts([text])[0]
