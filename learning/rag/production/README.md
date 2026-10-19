# Retrieval-Augmented Generation (RAG)

This learning path covers the complete RAG lifecycle and includes an offline, end-to-end baseline plus separate semantic indexing examples for Chroma, Pinecone, and Weaviate.

## Seven-step RAG lifecycle

1. **Ingestion and processing:** read source data, normalize it, attach source/tenant/access metadata, and record a version.
2. **Chunking and embeddings:** split at paragraph/sentence boundaries with overlap; embed document and query text using the same model and version.
3. **Indexing:** store vectors, text, stable chunk IDs, source metadata, and access filters.
4. **Query processing:** validate and normalize the user query; optionally route it or create query variants.
5. **Retrieval:** use dense vector, sparse/BM25, hybrid, filters, and/or reranking as the evaluation supports.
6. **Context augmentation:** select relevant, authorized chunks within a context budget and preserve citations.
7. **Generation:** answer only from evidence, abstain when unsupported, return source references, and evaluate the response.

## POCs

- [Offline full pipeline](pipeline/README.md): ingestion -> sentence-aware chunking -> sparse retrieval -> context selection -> extractive, cited answer. No network or API keys required.
- [Chroma](stores/chroma/README.md): local persistent vector collection with OpenAI embeddings.
- [Pinecone](stores/pinecone/README.md): cloud index upsert and vector search with OpenAI embeddings.
- [Weaviate](stores/weaviate/README.md): local persistent vector database and near-vector search with OpenAI embeddings.
- [Advanced retrieval](advanced/README.md): runnable query routing, multi-query retrieval, sentence compression, iterative retrieval, and offline retrieval evaluation examples.

The offline baseline deliberately uses a sparse lexical retriever and extractive answer so its behavior is inspectable. It is not semantic search or a quality substitute for an LLM. The three vector-store examples demonstrate embedding/index APIs separately; wire one into the pipeline only after matching the embedding model, metadata filters, and evaluation.

## Tools and framework choices by maturity

| Concern | Basic POC | Prototype | Enterprise |
|---|---|---|---|
| Loading/parsing | Python, JSON/TXT, `pathlib` | Unstructured, Docling, LlamaIndex readers, LangChain loaders | Airflow/Dagster, Kafka, SharePoint/S3/Blob connectors, document lifecycle APIs |
| Chunking | Sentence/paragraph-aware Python splitter | LangChain text splitters, LlamaIndex `SentenceSplitter`, semantic chunking experiments | Versioned chunk policy, language/document-type-aware parsing, reproducible re-index jobs |
| Embeddings | OpenAI Embeddings API or local Sentence Transformers | Provider APIs, Hugging Face, Ollama; batched embedding jobs | Approved model gateway, model/version registry, privacy controls, quotas and embedding cache |
| Index and vector store | Chroma local / FAISS | Pinecone, Weaviate, Qdrant, Milvus, managed Chroma | HA managed database, tenant/ACL filters, backup/restore, index migration and residency controls |
| Retrieval | Top-k dense or BM25 | Hybrid search, query expansion, metadata filters, rerankers | Offline/online evaluation, access-aware retrieval, query routing, shadow rollout |
| Orchestration | This Python pipeline | LangChain, LlamaIndex, LangGraph | LangGraph/FastAPI services, durable jobs, explicit timeouts/retries and audit |
| Generation | Extractive answer | GPT/Claude/Gemini/Llama with citations and abstention | Approved provider gateway, structured output, safety review, rate/cost budgets |
| Evaluation | Labeled query/source fixtures | Ragas, DeepEval, Phoenix/LangSmith evaluations | Versioned datasets, CI release gates, human review, drift monitoring and SLOs |
| Operations | Local files and logs | OpenTelemetry + LangSmith/Langfuse/Phoenix | Centralized traces/metrics/logs, privacy redaction, on-call, retention and DR |

Choose one component at a time based on corpus size, access-control needs, latency, cost, residency, and measured retrieval quality. Pinecone, Weaviate, and Chroma are independent examples, not dependencies to deploy together.

## Applications

| Use case | Example sources | Important controls |
|---|---|---|
| Customer support | Approved product docs, FAQs, release notes | Cite current versions; route account-specific questions to authorized systems |
| Legal/compliance | Contracts, regulations, case material | Preserve jurisdiction/date/provenance; attorney review; strict matter-level access |
| Healthcare | Approved clinical guidelines and research | Clinical review; source/date visibility; patient privacy; no autonomous diagnosis |
| Enterprise knowledge | Policies, runbooks, engineering documentation | Apply source ACLs before retrieval; tenant/department scope; deletion propagation |

Use synthetic public sample text for POCs. Legal and healthcare are high-impact domains and need domain governance and expert validation before any user-facing use.

## RAG-specific evaluation and operational checklist

- Retrieval: recall@k, precision@k, MRR/nDCG, citation/source accuracy, ACL leakage tests.
- Generation: faithfulness to retrieved evidence, answer relevance, abstention quality, completeness, human task success.
- Data: parser failures, stale/deleted documents, duplicate chunks, tenant/source/version metadata, re-index rollback.
- Runtime: embedding/retrieval/generation latency separately, token counts, provider/database errors, cache hit rate and total cost.
- Safety/privacy: content treated as untrusted; authorization applied at retrieval time; no prompt content or secrets in ordinary logs.
- Release: compare a versioned query/source/reference dataset against a baseline before swapping chunking, embedding, index, prompt, or model.

BLEU/ROUGE/BERTScore can help compare text similarity but do not by themselves establish factual grounding. No single RAG score is enough for release.

## Advanced techniques

See [advanced retrieval POC](advanced/README.md) for working, local examples of query routing, multi-query retrieval, compression, iterative retrieval, and metrics. Other techniques to evaluate include:

- **Hybrid search:** combine dense semantic retrieval with sparse/BM25 keyword search, especially for exact names, IDs, and policy terms.
- **Multi-query retrieval:** expand/rephrase the query, retrieve per variant, and fuse ranked results; avoid unbounded model-generated variants.
- **Contextual compression:** filter or rerank retrieved passages and keep only evidence-bearing sentences.
- **Query routing:** choose a domain, retriever, or index based on the request, while applying independent access controls.
- **Iterative/agentic RAG:** retrieve, inspect evidence, and retrieve again for multi-hop questions; use bounded steps, tool allowlists, and explicit stopping rules.
- **Multimodal RAG:** parse and retrieve images, tables, audio, or video using modality-appropriate encoders and source references.
- **Graph RAG:** retrieve entities/relationships from a governed knowledge graph alongside text passages.
- **Personalized RAG:** use only authorized user/profile context and provide a way to inspect, correct, and delete retained preferences.

Hybrid search and learned reranking depend on an embedding/model/index backend and should be evaluated against the same labeled queries. Every extra retrieval or model call adds latency, cost, and failure modes.
