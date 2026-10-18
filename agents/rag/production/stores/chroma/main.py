"""Index and query synthetic policy chunks with persistent local Chroma."""

import os
import sys
from pathlib import Path

import chromadb

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
            'Usage: python -m agents.rag.production.stores.chroma.main "question" [--demo]'
        )

    chunks = chunk_documents()
    path = Path(os.environ.get("CHROMA_PATH", "agents/rag/.chroma_data"))
    path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(path))
    collection = client.get_or_create_collection(
        name=os.environ.get("CHROMA_COLLECTION", "policy_chunks"),
        metadata={"hnsw:space": "cosine"},
    )

    vectors = embed_texts([chunk.text for chunk in chunks])
    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=vectors,
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {
                "document_id": chunk.document_id,
                "version": chunk.version,
                "use_case": chunk.use_case,
            }
            for chunk in chunks
        ],
    )
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=min(3, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    for index, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][index] or {}
        document = results["documents"][0][index] or ""
        distance = results["distances"][0][index]
        print(
            f"[{metadata.get('document_id')} v{metadata.get('version')} "
            f"#{chunk_id}] distance={distance:.4f} {document}"
        )
    client.close()


if __name__ == "__main__":
    main()
