# Agent With Vector Search

This example ranks an in-memory product catalog using sparse word-count vectors and cosine similarity. It needs only the Python standard library and writes no index or data to disk.

Run from the repository root:

```powershell
python -m agents.vector.agent_vector_product_search --demo
python -m agents.vector.agent_vector_product_search
```

This demonstrates vector similarity, not semantic embeddings: related words such as `notebook` and `laptop` will not match unless they share terms. Production semantic search typically uses an embedding model and a vector database or an in-memory vector index. This example intentionally avoids those dependencies and persistence.

## Vector storage architecture POCs

The following examples use semantic embeddings from OpenAI and synthetic catalog content. Each case has its own dependencies and setup guide:

- [In-memory vector store cache](cache/README.md): ephemeral Chroma index for hot data.
- [Persistent vector database](database/README.md): Qdrant local storage as the durable source of truth.
- [Tiered cache and database](tiered/README.md): Chroma cache lookup, persistent Qdrant fallback, and cache promotion.

These POCs require `OPENAI_API_KEY` to generate embeddings. They are intentionally separate from the standard-library-only example above.

To run the offline integration tests, install the vector POC dependencies into one environment:

```powershell
python -m pip install -r agents\vector\cache\requirements.txt `
  -r agents\vector\database\requirements.txt `
  -r agents\vector\tiered\requirements.txt
python -m unittest agents.vector.test_vector_pocs -v
```

The tests replace the embedding API with deterministic vectors and use temporary Qdrant storage; they do not require an API key or a running service.
