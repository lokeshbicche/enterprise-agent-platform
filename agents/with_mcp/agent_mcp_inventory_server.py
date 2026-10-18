"""MCP server exposing a read-only, in-memory inventory tool."""

from mcp.server import MCPServer


mcp = MCPServer(
    "sample-inventory",
    instructions="Provides read-only inventory lookups for sample SKUs.",
)
_INVENTORY = {
    "SKU-100": {"name": "Desk lamp", "quantity": 12},
    "SKU-200": {"name": "USB-C hub", "quantity": 4},
}


@mcp.tool()
def check_inventory(sku: str) -> str:
    """Return the sample stock count for a SKU."""
    item = _INVENTORY.get(sku.strip().upper())
    if item is None:
        return f"SKU {sku} was not found in the in-memory inventory."
    return f"{item['name']} ({sku.upper()}): {item['quantity']} units in stock."


if __name__ == "__main__":
    mcp.run()
