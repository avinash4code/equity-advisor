# ABOUTME: v3 live-data node -- pulls current market/financial data via the market_data MCP server.

from equity_agent.mcp.client import fetch_live_financials
from equity_agent.state import AgentState


def live_data_node(state: AgentState) -> dict:
    """Fetches live quarterly financials for state['ticker'] via MCP."""
    return {"live_data": fetch_live_financials(state["ticker"])}
