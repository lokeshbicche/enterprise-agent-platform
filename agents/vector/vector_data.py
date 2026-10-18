"""Small synthetic catalog shared by the vector-storage POCs."""

from typing import TypedDict


class CatalogItem(TypedDict):
    id: str
    title: str
    text: str


CATALOG: list[CatalogItem] = [
    {
        "id": "travel-laptop",
        "title": "Travel laptop",
        "text": (
            "Lightweight business laptop with long battery life, "
            "portable design, and a durable metal case."
        ),
    },
    {
        "id": "ergonomic-chair",
        "title": "Ergonomic office chair",
        "text": (
            "Adjustable desk chair with lumbar support, breathable mesh, "
            "and settings for comfortable all-day work."
        ),
    },
    {
        "id": "noise-cancelling-headphones",
        "title": "Noise-cancelling headphones",
        "text": (
            "Wireless headphones that reduce background noise during "
            "commutes and focused work."
        ),
    },
    {
        "id": "usb-c-dock",
        "title": "USB-C docking station",
        "text": (
            "Laptop dock with multiple monitor outputs, Ethernet, "
            "and USB ports for a desktop workspace."
        ),
    },
]


def get_item(item_id: str) -> CatalogItem:
    """Return a catalog item by ID or raise if it does not exist."""

    for item in CATALOG:
        if item["id"] == item_id:
            return item
    raise KeyError(f"Unknown catalog item: {item_id}")
