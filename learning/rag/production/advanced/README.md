# Advanced retrieval and evaluation POC

These dependency-free examples expose techniques as measurable retrieval behaviors, not as promises of higher answer quality:

- **Query routing:** selects an HR or finance corpus filter based on explicit query terms. Production authorization must still come from authenticated identity and trusted ACL metadata, not this heuristic.
- **Multi-query retrieval:** creates simple deterministic synonym variants and fuses ranked results with reciprocal-rank fusion.
- **Contextual compression:** retains query-relevant sentences while keeping source IDs and versions.
- **Iterative retrieval:** uses terms from first-pass evidence to make a second sparse retrieval pass.
- **Evaluation:** reports precision@k, recall@k, and MRR against expected source IDs.

```powershell
python -m agents.rag.production.advanced.main --demo
python -m unittest agents.rag.production.test_rag -v
```

For production, compare hybrid dense+sparse retrieval, query expansion, reranking, and compression against the same versioned evaluation set. Do not trust query-generated variants or retrieved text as instructions; treat them as untrusted content.
