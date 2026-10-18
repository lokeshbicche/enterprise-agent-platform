# Agent With Vector Search

This example ranks an in-memory product catalog using sparse word-count vectors and cosine similarity. It needs only the Python standard library and writes no index or data to disk.

Run from the repository root:

```powershell
python -m agents.with_vector.agent_vector_product_search --demo
python -m agents.with_vector.agent_vector_product_search
```

This demonstrates vector similarity, not semantic embeddings: related words such as `notebook` and `laptop` will not match unless they share terms. Production semantic search typically uses an embedding model and a vector database or an in-memory vector index. This example intentionally avoids those dependencies and persistence.
