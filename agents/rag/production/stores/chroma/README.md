# Chroma semantic RAG index

This standalone example chunks synthetic HR/finance documents, creates embeddings, stores the vectors and source metadata in a persistent local Chroma collection, and retrieves the nearest chunks. It uses the Chroma client directly and OpenAI's Embeddings API.

```powershell
python -m venv .venv-rag-chroma
.\.venv-rag-chroma\Scripts\Activate.ps1
python -m pip install -r agents\rag\production\stores\chroma\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.rag.production.stores.chroma.main --demo
```

Set `CHROMA_PATH` to change local persistence, `CHROMA_COLLECTION` to select the collection, and `EMBEDDING_MODEL` to select the same model for indexing and queries. Local persistent Chroma is a developer POC, not a multi-replica production service.
