# Agent With MCP

This example demonstrates an agent client discovering and calling an inventory tool exposed by a separate MCP server. The client launches the server as a local subprocess and communicates over MCP stdio. The sample inventory exists only in server memory; no database, model, API key, or persistent file is used.

MCP standardizes tool/context connections; it does not decide which tool to use. This small client checks that `check_inventory` is offered, then calls it for the requested SKU.

## Install and run

The current MCP Python SDK requires Python 3.11 or newer. From the repository root:

```powershell
python -m pip install "mcp[cli]"
python -m agents.with_mcp.agent_mcp_inventory_client --demo
```

The demo queries `SKU-100`. To look up another SKU, pass it as an argument:

```powershell
python -m agents.with_mcp.agent_mcp_inventory_client SKU-200
```

- [MCP client](agent_mcp_inventory_client.py)
- [MCP inventory server](agent_mcp_inventory_server.py)
