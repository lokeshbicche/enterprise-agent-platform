"""Upsert and query synthetic policy chunks in a Pinecone serverless index."""

import os
import sys
import time

from pinecone import Pinecone, ServerlessSpec

from agents.rag.production.pipeline.main import chunk_documents
from agents.vector.embeddings import embed_text, embed_texts


def main() -> None:
    query = (
        "How many paid leave days do full-time employees receive?"
        if "--demo" in sys.argv[1:]
        else " ".join(argument for argument in sys.argv[1:] if argument != "--demo")
    )
    if not query.strip():
        raise SystemExit(
            'Usage: python -m agents.rag.production.stores.pinecone.main "question" [--demo]'
        )

    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        raise SystemExit("Set PINECONE_API_KEY before using the Pinecone POC.")
    index_name = os.environ.get("PINECONE_INDEX", "enterprise-rag-poc")
    client = Pinecone(api_key=api_key)
    chunks = chunk_documents()
    vectors = embed_texts([chunk.text for chunk in chunks])
    if not client.has_index(index_name):
        client.create_index(
            name=index_name,
            dimension=len(vectors[0]),
            metric="cosine",
            spec=ServerlessSpec(
                cloud=os.environ.get("PINECONE_CLOUD", "aws"),
                region=os.environ.get("PINECONE_REGION", "us-east-1"),
            ),
        )
        deadline = time.monotonic() + 120
        while not client.describe_index(index_name).status["ready"]:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Pinecone index {index_name!r} was not ready in time.")
            time.sleep(2)

    index = client.Index(index_name)
    index.upsert(
        vectors=[
            (
                chunk.chunk_id,
                vector,
                {
                    "document_id": chunk.document_id,
                    "version": chunk.version,
                    "use_case": chunk.use_case,
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ],
        namespace=os.environ.get("PINECONE_NAMESPACE", "rag-poc"),
    )
    response = index.query(
        vector=embed_text(query),
        top_k=3,
        include_metadata=True,
        namespace=os.environ.get("PINECONE_NAMESPACE", "rag-poc"),
    )
    for match in response.matches:
        metadata = match.metadata or {}
        print(
            f"[{metadata.get('document_id')} v{metadata.get('version')} "
            f"#{match.id}] score={match.score:.4f} {metadata.get('text', '')}"
        )


if __name__ == "__main__":
    main()
