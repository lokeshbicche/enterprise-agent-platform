"""Search hot catalog entries in an ephemeral Chroma vector store."""

import sys

import chromadb

from agents.vector.embeddings import embed_text
from agents.vector.vector_data import CATALOG


def main() -> None:
    demo = "--demo" in sys.argv[1:]
    query = " ".join(argument for argument in sys.argv[1:] if argument != "--demo")
    if not demo and not query.strip():
        raise SystemExit(
            'Usage: python -m agents.vector.cache.main "search query" [--demo]'
        )
    if demo:
        query = "portable computer for business travel"

    client = chromadb.EphemeralClient()
    try:
        collection = client.create_collection(
            name="hot_catalog",
            metadata={"hnsw:space": "cosine"},
        )
        collection.add(
            ids=[item["id"] for item in CATALOG],
            embeddings=[embed_text(item["text"]) for item in CATALOG],
            documents=[item["text"] for item in CATALOG],
            metadatas=[{"title": item["title"]} for item in CATALOG],
        )

        result = collection.query(
            query_embeddings=[embed_text(query)],
            n_results=1,
            include=["documents", "metadatas", "distances"],
        )
        if not result["ids"][0]:
            print("No matching items.")
            return

        metadata = result["metadatas"][0][0] or {}
        document = result["documents"][0][0] or ""
        distance = result["distances"][0][0]
        print(f"Vector-store cache | distance={distance:.4f}")
        print(f"{metadata.get('title', 'Untitled')}: {document}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
