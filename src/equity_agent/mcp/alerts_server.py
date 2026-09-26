# ABOUTME: MCP server exposing an outbound alert tool. Stub delivery (logs only) --
# ABOUTME: swap for a real channel (Slack/email/etc.) later.
# ABOUTME: Run standalone for manual testing; normally spawned over stdio by mcp/client.py.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("alerts")


@mcp.tool()
def send_alert(ticker: str, message: str) -> dict:
    """Sends an alert for `ticker`. Currently logs to stdout; delivery channel TBD."""
    print(f"[ALERT] {ticker}: {message}")
    return {"sent": True, "ticker": ticker, "message": message}


if __name__ == "__main__":
    mcp.run(transport="stdio")
