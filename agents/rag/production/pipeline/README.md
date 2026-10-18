# Offline end-to-end RAG baseline

This dependency-free demo implements the seven stages with a deterministic pipeline:

1. Loads versioned synthetic policy documents.
2. Cleans and sentence/paragraph-aware chunks them with overlap.
3. Uses a transparent sparse term-frequency/IDF retriever.
4. Validates/normalizes the query.
5. Ranks the chunks and retains relevant evidence.
6. Builds a bounded context with source IDs.
7. Returns an extractive answer with citations, or abstains.

Because it uses lexical retrieval and extractive generation, it is suitable for learning and repeatable tests—not semantic embedding or a user-facing assistant.

```powershell
python -m agents.rag.production.pipeline.main --demo
python -m agents.rag.production.pipeline.main "How many vacation days do full-time employees receive?"
python -m unittest agents.rag.production.test_rag -v
```

To use hosted generation instead of the default extractive answer, install the OpenAI SDK, set credentials, and pass `--llm`:

```powershell
python -m pip install "openai>=1"
$env:OPENAI_API_KEY = "your-provider-key"
python -m agents.rag.production.pipeline.main --demo --llm
```

This sends the query and retrieved excerpts to the configured provider. Do not use with sensitive documents until data handling, provider approval, and access-control requirements are addressed. The code abstains if retrieval returns no context; hosted calls can still fail and surface an error.

For semantic search, see the separate [Chroma](../stores/chroma/README.md), [Pinecone](../stores/pinecone/README.md), and [Weaviate](../stores/weaviate/README.md) examples.
