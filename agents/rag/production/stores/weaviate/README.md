# Weaviate semantic RAG index

This example uses the Weaviate Python client with a local persistent embedded database and externally generated OpenAI vectors. The Weaviate client manages its local embedded database process; no cloud credentials are required.

The client may need to download the Weaviate runtime the first time it starts. Embeddings still require outbound access to the configured OpenAI API.

```powershell
python -m venv .venv-rag-weaviate
.\.venv-rag-weaviate\Scripts\Activate.ps1
python -m pip install -r agents\rag\production\stores\weaviate\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.rag.production.stores.weaviate.main --demo
```

Set `WEAVIATE_PERSISTENCE_PATH` to choose local storage. For shared environments, provision Weaviate Cloud or a secured cluster and use verified authentication/TLS; embedded mode is for a local POC.
