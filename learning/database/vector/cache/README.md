# In-memory vector store cache

This POC uses Chroma's ephemeral client as a small, process-local semantic index for hot catalog entries. It disappears when the process exits. It demonstrates a fast in-memory vector store, not a durable source of truth.

Embeddings are generated with OpenAI's `text-embedding-3-small` model. Set `EMBEDDING_MODEL` to override it and `OPENAI_API_KEY` to authenticate.

The vector lookup is in memory, but this example still makes a network call to embed each query; that call can dominate end-to-end latency. Measure the whole request path and consider a local embedding model or a separately cached embedding service for a real latency-sensitive system.

```powershell
python -m venv .venv-vector-cache
.\.venv-vector-cache\Scripts\Activate.ps1
python -m pip install -r agents\vector\cache\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.vector.cache.main --demo
python -m agents.vector.cache.main "portable computer for travel"
```

The example indexes the synthetic catalog at startup, runs a semantic similarity query, and prints the nearest item and cosine distance. All catalog data is sample data.
