"""In-memory RAG-style HR policy assistant using only the Python standard library."""

import re
import sys
from typing import Dict, List, Set, Tuple


_DOCUMENTS = [
    {
        "source": "leave-policy",
        "text": "Full-time employees receive 20 paid leave days per calendar year. Unused days do not roll over.",
    },
    {
        "source": "remote-work-policy",
        "text": "Employees may work remotely up to three days each week with manager approval.",
    },
    {
        "source": "travel-policy",
        "text": "Submit business travel expenses with receipts within 30 days of completing the trip.",
    },
]
_STOP_WORDS = {"a", "an", "and", "are", "do", "does", "for", "get", "how", "i", "in", "is", "may", "of", "the", "to", "what", "when", "with"}


def _tokens(text: str) -> Set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2 and word not in _STOP_WORDS}


def retrieve(query: str, limit: int = 2) -> List[Tuple[float, Dict[str, str]]]:
    """Retrieve in-memory policy passages by simple query-term overlap."""
    query_terms = _tokens(query)
    if not query_terms:
        return []

    ranked = []
    for document in _DOCUMENTS:
        overlap = query_terms & _tokens(document["text"])
        score = len(overlap) / len(query_terms)
        if score >= 0.3:
            ranked.append((score, document))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[:limit]


class HRPolicyAgent:
    """Retrieve relevant passages and answer using only that retrieved evidence."""

    def run(self, question: str) -> str:
        matches = retrieve(question)
        if not matches:
            return "I couldn't find relevant information in the in-memory policy examples."

        evidence = "\n".join(
            f"- [{document['source']}] {document['text']}"
            for _, document in matches
        )
        return f"Relevant policy information:\n{evidence}"


def main() -> None:
    agent = HRPolicyAgent()
    if "--demo" in sys.argv[1:]:
        question = "How many paid leave days do full-time employees get?"
    else:
        question = input("Ask an HR policy question: ").strip()
    print(agent.run(question))


if __name__ == "__main__":
    main()
