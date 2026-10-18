"""Runnable local examples of query routing, expansion, compression, and evaluation."""

import json
import sys

from agents.rag.production.pipeline.main import (
    DOCUMENTS,
    Chunk,
    chunk_documents,
    retrieve,
    tokenize,
)


SYNONYMS = {
    "leave": "vacation",
    "vacation": "leave",
    "expense": "reimbursement",
    "reimbursement": "expense",
    "remote": "telecommuting",
    "telecommuting": "remote",
}


def route_query(query: str) -> set[str] | None:
    terms = set(tokenize(query))
    if terms & {"travel", "expense", "expenses", "receipt", "receipts"}:
        return {"finance"}
    if terms & {"leave", "vacation", "remote", "employee", "employees"}:
        return {"hr"}
    return None


def query_variants(query: str) -> list[str]:
    terms = tokenize(query)
    variants = [query]
    for term in terms:
        synonym = SYNONYMS.get(term)
        if synonym:
            variants.append(" ".join(synonym if item == term else item for item in terms))
    return list(dict.fromkeys(variants))


def multi_query_retrieve(
    query: str,
    chunks: list[Chunk],
    limit: int = 3,
    allowed_use_cases: set[str] | None = None,
) -> list[tuple[float, Chunk]]:
    fused: dict[str, tuple[float, Chunk]] = {}
    for variant in query_variants(query):
        matches = retrieve(
            variant,
            chunks,
            limit=limit,
            allowed_use_cases=allowed_use_cases,
        )
        for rank, (score, chunk) in enumerate(matches, start=1):
            previous_score = fused.get(chunk.chunk_id, (0.0, chunk))[0]
            fused[chunk.chunk_id] = (previous_score + 1 / (60 + rank), chunk)
    ranked = sorted(fused.values(), key=lambda item: (-item[0], item[1].chunk_id))
    return ranked[:limit]


def compress_results(
    query: str,
    results: list[tuple[float, Chunk]],
) -> list[tuple[float, Chunk]]:
    query_terms = set(tokenize(query))
    compressed: list[tuple[float, Chunk]] = []
    for score, chunk in results:
        sentences = [
            sentence
            for sentence in chunk.text.split(". ")
            if query_terms & set(tokenize(sentence))
        ]
        if sentences:
            text = ". ".join(sentences)
            if not text.endswith((".", "!", "?")):
                text += "."
            compressed.append(
                (
                    score,
                    Chunk(
                        chunk.chunk_id,
                        chunk.document_id,
                        chunk.version,
                        text,
                        chunk.use_case,
                    ),
                )
            )
    return compressed


def iterative_retrieve(
    query: str,
    chunks: list[Chunk],
    limit: int = 3,
    allowed_use_cases: set[str] | None = None,
) -> list[tuple[float, Chunk]]:
    first_pass = retrieve(
        query,
        chunks,
        limit=limit,
        allowed_use_cases=allowed_use_cases,
    )
    if not first_pass:
        return []
    initial_terms = set(tokenize(query))
    follow_up_terms = [
        term
        for term in tokenize(" ".join(chunk.text for _, chunk in first_pass))
        if term not in initial_terms
    ]
    if not follow_up_terms:
        return first_pass
    second_pass = retrieve(
        " ".join(follow_up_terms[:8]),
        chunks,
        limit=limit,
        allowed_use_cases=allowed_use_cases,
    )
    merged: dict[str, tuple[float, Chunk]] = {
        chunk.chunk_id: (score, chunk) for score, chunk in first_pass
    }
    for score, chunk in second_pass:
        previous = merged.get(chunk.chunk_id)
        if previous is None:
            merged[chunk.chunk_id] = (score * 0.5, chunk)
    ranked = sorted(merged.values(), key=lambda item: (-item[0], item[1].chunk_id))
    return ranked[:limit]


def evaluate_retrieval(
    fixtures: list[tuple[str, set[str]]],
    chunks: list[Chunk],
    limit: int = 3,
) -> dict[str, float]:
    if not fixtures:
        raise ValueError("At least one evaluation fixture is required.")
    precision_total = recall_total = reciprocal_rank_total = 0.0
    for query, expected_ids in fixtures:
        if not expected_ids:
            raise ValueError("Each evaluation fixture needs an expected source ID.")
        results = retrieve(query, chunks, limit=limit)
        actual_ids = [chunk.document_id for _, chunk in results]
        relevant = sum(source_id in expected_ids for source_id in actual_ids)
        precision_total += relevant / limit
        recall_total += relevant / len(expected_ids)
        reciprocal_rank_total += next(
            (
                1 / rank
                for rank, source_id in enumerate(actual_ids, start=1)
                if source_id in expected_ids
            ),
            0.0,
        )
    count = len(fixtures)
    return {
        f"precision@{limit}": round(precision_total / count, 4),
        f"recall@{limit}": round(recall_total / count, 4),
        "mrr": round(reciprocal_rank_total / count, 4),
    }


def demo() -> dict[str, object]:
    chunks = chunk_documents(DOCUMENTS)
    query = "How many vacation days do full-time employees receive?"
    route = route_query(query)
    variants = query_variants(query)
    results = multi_query_retrieve(
        query,
        chunks,
        allowed_use_cases=route,
    )
    compressed = compress_results(query, results)
    iterative = iterative_retrieve(
        query,
        chunks,
        allowed_use_cases=route,
    )
    metrics = evaluate_retrieval(
        [
            ("How many paid leave days?", {"leave-policy"}),
            ("When are travel expenses due?", {"travel-policy"}),
        ],
        chunks,
    )
    return {
        "query": query,
        "route_filter_demo_only": sorted(route) if route else None,
        "query_variants": variants,
        "multi_query_results": [
            {"source": chunk.document_id, "text": chunk.text, "fusion_score": score}
            for score, chunk in results
        ],
        "compressed_results": [
            {"source": chunk.document_id, "text": chunk.text}
            for _, chunk in compressed
        ],
        "iterative_sources": [chunk.document_id for _, chunk in iterative],
        "offline_retrieval_metrics": metrics,
    }


def main() -> None:
    if "--demo" not in sys.argv[1:]:
        raise SystemExit("Run this teaching example with --demo.")
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
