"""A basic MCP client that discovers and calls an inventory tool over stdio."""

import sys


def _read_text(result, text_content_type) -> str:
    return "\n".join(
        block.text
        for block in result.content
        if isinstance(block, text_content_type)
    )


async def run_agent(sku: str) -> None:
    try:
        from mcp import Client, StdioServerParameters
        from mcp.types import TextContent
    except ImportError as exc:
        raise SystemExit(
            'Install the MCP Python SDK with: python -m pip install "mcp[cli]"'
        ) from exc

    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agents.with_mcp.agent_mcp_inventory_server"],
    )
    async with Client(server) as client:
        available_tools = await client.list_tools()
        tool_names = {tool.name for tool in available_tools.tools}
        if "check_inventory" not in tool_names:
            print("The MCP server does not provide check_inventory.")
            return

        result = await client.call_tool("check_inventory", {"sku": sku})
        if result.is_error:
            print("The inventory tool returned an error:")
        print(_read_text(result, TextContent) or "The MCP tool returned no text.")


def main() -> None:
    arguments = sys.argv[1:]
    if "--demo" in arguments:
        sku = "SKU-100"
    elif arguments:
        sku = arguments[0]
    else:
        sku = input("Enter an inventory SKU: ").strip()

    try:
        import anyio
    except ImportError as exc:
        raise SystemExit(
            'Install the MCP Python SDK with: python -m pip install "mcp[cli]"'
        ) from exc
    anyio.run(run_agent, sku)


if __name__ == "__main__":
    main()
