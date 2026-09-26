# ABOUTME: MCP client config and sync wrapper for calling the market-data server's tool.

import asyncio
import json
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

MARKET_DATA_SERVER_SCRIPT = Path(__file__).resolve().parent / "market_data_server.py"
ALERTS_SERVER_SCRIPT = Path(__file__).resolve().parent / "alerts_server.py"

_CONNECTIONS = {
    "market_data": {
        "command": "python",
        "args": [str(MARKET_DATA_SERVER_SCRIPT)],
        "transport": "stdio",
    },
    "alerts": {
        "command": "python",
        "args": [str(ALERTS_SERVER_SCRIPT)],
        "transport": "stdio",
    },
}


async def _call_tool_async(server_name: str, tool_name: str, **kwargs) -> dict:
    client = MultiServerMCPClient(_CONNECTIONS)
    tools = await client.get_tools(server_name=server_name)
    tool = next(t for t in tools if t.name == tool_name)
    content_blocks = await tool.ainvoke(kwargs)
    text = next(block["text"] for block in content_blocks if block["type"] == "text")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"MCP tool {tool_name!r} ({kwargs}) returned non-JSON: {text}") from e


def fetch_live_financials(ticker: str) -> dict:
    """Synchronous wrapper -- LangGraph node functions in this project are sync."""
    return asyncio.run(_call_tool_async("market_data", "get_quarterly_financials", ticker=ticker))


def fetch_live_price(ticker: str) -> dict:
    """Lightweight current price + shares outstanding, independent of report freshness."""
    return asyncio.run(_call_tool_async("market_data", "get_price", ticker=ticker))


def send_alert(ticker: str, message: str) -> dict:
    """Synchronous wrapper around the alerts server's send_alert tool."""
    return asyncio.run(_call_tool_async("alerts", "send_alert", ticker=ticker, message=message))
