# Persistent vector database

This POC stores complete synthetic catalog records and their embeddings in Qdrant's local persistent mode. Data remains on disk between runs in `.qdrant_data/`. Local mode is for a single process/developer POC; use a managed or server Qdrant deployment for concurrent production services.

Embeddings use OpenAI's `text-embedding-3-small`. Set `OPENAI_API_KEY` and optionally `EMBEDDING_MODEL`.

```powershell
python -m venv .venv-vector-db
.\.venv-vector-db\Scripts\Activate.ps1
python -m pip install -r agents\vector\database\requirements.txt
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.vector.database.main --demo
python -m agents.vector.database.main "a quiet headset for commuting"
```

The program upserts the sample catalog on each invocation and queries the persistent Qdrant collection. To reset the local POC data, stop all processes using it and remove only the `agents\vector\.qdrant_data` directory.
