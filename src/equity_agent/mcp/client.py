# ABOUTME: MCP client config and sync wrapper for calling the market-data server's tool.

import asyncio
import json
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

SERVER_SCRIPT = Path(__file__).resolve().parent / "market_data_server.py"

_CONNECTIONS = {
    "market_data": {
        "command": "python",
        "args": [str(SERVER_SCRIPT)],
        "transport": "stdio",
    }
}


async def _call_tool_async(tool_name: str, ticker: str) -> dict:
    client = MultiServerMCPClient(_CONNECTIONS)
    tools = await client.get_tools(server_name="market_data")
    tool = next(t for t in tools if t.name == tool_name)
    content_blocks = await tool.ainvoke({"ticker": ticker})
    text = next(block["text"] for block in content_blocks if block["type"] == "text")
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"MCP tool {tool_name!r} for {ticker!r} returned non-JSON: {text}") from e


def fetch_live_financials(ticker: str) -> dict:
    """Synchronous wrapper -- LangGraph node functions in this project are sync."""
    return asyncio.run(_call_tool_async("get_quarterly_financials", ticker))


def fetch_live_price(ticker: str) -> dict:
    """Lightweight current price + shares outstanding, independent of report freshness."""
    return asyncio.run(_call_tool_async("get_price", ticker))
