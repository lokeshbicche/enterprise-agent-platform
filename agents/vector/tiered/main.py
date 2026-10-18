"""Use ephemeral Chroma as a hot query cache over persistent Qdrant."""

import os
import sys
from pathlib import Path
from uuid import uuid4

import chromadb
from qdrant_client import QdrantClient, models

from agents.vector.embeddings import embed_text, embed_texts
from agents.vector.vector_data import CATALOG

COLLECTION = "product_catalog"
CACHE_DISTANCE_THRESHOLD = 0.12


def open_database(vector_size: int) -> QdrantClient:
    storage_path = Path(
        os.environ.get("QDRANT_PATH", "agents/vector/.qdrant_data")
    )
    storage_path.mkdir(parents=True, exist_ok=True)
    client = QdrantClient(path=str(storage_path))
    if not client.collection_exists(COLLECTION):
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )
    if client.count(collection_name=COLLECTION, exact=True).count == 0:
        catalog_vectors = embed_texts([item["text"] for item in CATALOG])
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
    return client


def main() -> None:
    demo = "--demo" in sys.argv[1:]
    query = " ".join(argument for argument in sys.argv[1:] if argument != "--demo")
    if not demo and not query.strip():
        raise SystemExit(
            'Usage: python -m agents.vector.tiered.main "search query" [--demo]'
        )

    queries = (
        ["portable computer for business travel"] * 2
        if demo
        else [query]
    )
    cache_client = chromadb.EphemeralClient()
    try:
        cache = cache_client.create_collection(
            name="hot_query_cache",
            metadata={"hnsw:space": "cosine"},
        )
        query_vectors = [embed_text(query) for query in queries]
        database = open_database(len(query_vectors[0]))
        try:
            for current_query, query_vector in zip(queries, query_vectors):
                cached = cache.query(
                    query_embeddings=[query_vector],
                    n_results=1,
                    include=["documents", "metadatas", "distances"],
                )

                if cached["ids"][0] and cached["distances"][0][0] <= CACHE_DISTANCE_THRESHOLD:
                    metadata = cached["metadatas"][0][0] or {}
                    text = cached["documents"][0][0] or ""
                    print("CACHE HIT | " + current_query)
                    print(f"{metadata.get('title', 'Untitled')}: {text}")
                    continue

                result = database.query_points(
                    collection_name=COLLECTION,
                    query=query_vector,
                    limit=1,
                    with_payload=True,
                )
                if not result.points:
                    print("DATABASE MISS | " + current_query)
                    continue

                match = result.points[0]
                payload = match.payload or {}
                title = str(payload.get("title", "Untitled"))
                text = str(payload.get("text", ""))
                print(
                    f"CACHE MISS -> DATABASE | similarity={match.score:.4f} "
                    f"| {current_query}"
                )
                print(f"{title}: {text}")

                cache.upsert(
                    ids=[str(uuid4())],
                    embeddings=[query_vector],
                    documents=[text],
                    metadatas=[
                        {
                            "title": title,
                            "item_id": str(payload.get("item_id", "")),
                        }
                    ],
                )
        finally:
            database.close()
    finally:
        cache_client.close()


if __name__ == "__main__":
    main()
