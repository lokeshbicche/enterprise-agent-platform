# Agent With RAG

This standard-library example shows a small retrieval-augmented generation pipeline for HR policy questions. It retrieves relevant passages from hard-coded in-memory sample policies, then returns those passages as an extractive, evidence-grounded answer. It does not call an LLM, install extra packages, or write data to disk.

Run from the repository root:

```powershell
python -m agents.with_rag.agent_rag_hr_policy --demo
python -m agents.with_rag.agent_rag_hr_policy
```

The retriever uses simple term overlap so the steps are easy to inspect. It is not semantic search; see the [vector search examples](../vector/README.md) for vector stores and databases. For the complete RAG learning path—including the seven-stage offline pipeline, individual Chroma/Pinecone/Weaviate examples, advanced retrieval, use cases, evaluation, and POC-to-enterprise guidance—see [production RAG](production/README.md).

See [the example source](agent_rag_hr_policy.py).
