"""Index and query policy chunks with local persistent Weaviate."""

import os
import sys
import uuid

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import MetadataQuery

from agents.rag.production.pipeline.main import chunk_documents
from agents.vector.embeddings import embed_text, embed_texts

COLLECTION_NAME = "PolicyChunk"


def main() -> None:
    query = (
        "How many paid leave days do full-time employees receive?"
        if "--demo" in sys.argv[1:]
        else " ".join(argument for argument in sys.argv[1:] if argument != "--demo")
    )
    if not query.strip():
        raise SystemExit(
            'Usage: python -m agents.rag.production.stores.weaviate.main "question" [--demo]'
        )

    persistence_path = os.environ.get(
        "WEAVIATE_PERSISTENCE_PATH",
        "agents/rag/.weaviate_data",
    )
    client = weaviate.connect_to_embedded(persistence_data_path=persistence_path)
    try:
        if not client.collections.exists(COLLECTION_NAME):
            client.collections.create(
                name=COLLECTION_NAME,
                vector_config=Configure.Vectors.self_provided(),
                properties=[
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="version", data_type=DataType.TEXT),
                    Property(name="use_case", data_type=DataType.TEXT),
                    Property(name="text", data_type=DataType.TEXT),
                ],
            )
        collection = client.collections.get(COLLECTION_NAME)
        chunks = chunk_documents()
        vectors = embed_texts([chunk.text for chunk in chunks])
        for chunk, vector in zip(chunks, vectors, strict=True):
            collection.data.replace(
                uuid=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.chunk_id)),
                properties={
                    "document_id": chunk.document_id,
                    "version": chunk.version,
                    "use_case": chunk.use_case,
                    "text": chunk.text,
                },
                vector=vector,
            )

        response = collection.query.near_vector(
            near_vector=embed_text(query),
            limit=3,
            return_metadata=MetadataQuery(distance=True),
        )
        for item in response.objects:
            properties = item.properties
            distance = item.metadata.distance if item.metadata else None
            print(
                f"[{properties['document_id']} v{properties['version']} "
                f"#{item.uuid}] distance={distance} {properties['text']}"
            )
    finally:
        client.close()


if __name__ == "__main__":
    main()
