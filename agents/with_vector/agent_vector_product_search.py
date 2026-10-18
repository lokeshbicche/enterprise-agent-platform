"""In-memory product search using sparse word-count vectors and cosine similarity."""

import math
import re
import sys
from collections import Counter
from typing import Dict, List, Tuple


_PRODUCTS = [
    {
        "sku": "LAP-13",
        "name": "Travel laptop",
        "description": "Lightweight 13-inch laptop with a long battery life for business travel.",
    },
    {
        "sku": "MON-27",
        "name": "Office monitor",
        "description": "27-inch monitor with an adjustable stand for a comfortable desk setup.",
    },
    {
        "sku": "BAG-20",
        "name": "Laptop backpack",
        "description": "Padded backpack with a protected laptop sleeve and carry-on sizing.",
    },
]
_STOP_WORDS = {"a", "an", "and", "for", "in", "of", "the", "to", "with"}


def _vectorize(text: str) -> Counter:
    terms = [
        term
        for term in re.findall(r"[a-z0-9]+", text.lower())
        if len(term) > 1 and term not in _STOP_WORDS
    ]
    return Counter(terms)


def _cosine_similarity(left: Counter, right: Counter) -> float:
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    dot_product = sum(value * right.get(term, 0) for term, value in left.items())
    return dot_product / (left_norm * right_norm)


def search_products(query: str, limit: int = 3) -> List[Tuple[float, Dict[str, str]]]:
    """Rank the in-memory catalog by cosine similarity of term-frequency vectors."""
    query_vector = _vectorize(query)
    if not query_vector:
        return []

    ranked = []
    for product in _PRODUCTS:
        searchable_text = " ".join(product.values())
        score = _cosine_similarity(query_vector, _vectorize(searchable_text))
        if score > 0:
            ranked.append((score, product))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[:limit]


class ProductSearchAgent:
    def run(self, request: str) -> str:
        matches = search_products(request)
        if not matches:
            return "No matching products found in the in-memory catalog."
        return "\n".join(
            f"{product['sku']} | {product['name']} | score={score:.3f} | {product['description']}"
            for score, product in matches
        )


def main() -> None:
    agent = ProductSearchAgent()
    if "--demo" in sys.argv[1:]:
        query = "portable laptop for business travel"
    else:
        query = input("Describe the product you need: ").strip()
    print(agent.run(query))


if __name__ == "__main__":
    main()
