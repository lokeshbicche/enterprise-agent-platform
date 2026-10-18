# Pinecone semantic RAG index

This standalone example creates a serverless Pinecone index if needed, embeds synthetic policy chunks, upserts stable IDs and metadata, and queries the index. Configure the Pinecone API key and cloud region before running.

```powershell
python -m venv .venv-rag-pinecone
.\.venv-rag-pinecone\Scripts\Activate.ps1
python -m pip install -r agents\rag\production\stores\pinecone\requirements.txt
$env:PINECONE_API_KEY = "your-pinecone-key"
$env:PINECONE_CLOUD = "aws"
$env:PINECONE_REGION = "us-east-1"
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.rag.production.stores.pinecone.main --demo
```

The script waits for index readiness and derives the index dimension from the embedding response. Index creation is a provisioning operation: use a pre-created index, controlled migrations, least-privilege credentials, namespace/metadata ACL filters, and approved residency settings in production.
