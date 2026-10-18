"""Upsert and search catalog embeddings in persistent local Qdrant."""

import os
import sys
from pathlib import Path

from qdrant_client import QdrantClient, models

from agents.vector.embeddings import embed_text, embed_texts
from agents.vector.vector_data import CATALOG

COLLECTION = "product_catalog"


def main() -> None:
    demo = "--demo" in sys.argv[1:]
    query = " ".join(argument for argument in sys.argv[1:] if argument != "--demo")
    if not demo and not query.strip():
        raise SystemExit(
            'Usage: python -m agents.vector.database.main "search query" [--demo]'
        )
    if demo:
        query = "an adjustable comfortable desk chair"

    catalog_vectors = embed_texts([item["text"] for item in CATALOG])
    storage_path = Path(
        os.environ.get("QDRANT_PATH", "agents/vector/.qdrant_data")
    )
    storage_path.mkdir(parents=True, exist_ok=True)

    client = QdrantClient(path=str(storage_path))
    try:
        if not client.collection_exists(COLLECTION):
            client.create_collection(
                collection_name=COLLECTION,
                vectors_config=models.VectorParams(
                    size=len(catalog_vectors[0]),
                    distance=models.Distance.COSINE,
                ),
            )
        client.upsert(
            collection_name=COLLECTION,
            wait=True,
            points=[
                models.PointStruct(
                    id=index,
                    vector=catalog_vectors[index - 1],
                    payload={
                        "item_id": item["id"],
                        "title": item["title"],
                        "text": item["text"],
                    },
                )
                for index, item in enumerate(CATALOG, start=1)
            ],
        )
        response = client.query_points(
            collection_name=COLLECTION,
            query=embed_text(query),
            limit=1,
            with_payload=True,
        )
    finally:
        client.close()

    if not response.points:
        print("No matching items.")
        return

    match = response.points[0]
    payload = match.payload or {}
    print(f"Persistent Qdrant database | similarity={match.score:.4f}")
    print(f"{payload.get('title', 'Untitled')}: {payload.get('text', '')}")


if __name__ == "__main__":
    main()
