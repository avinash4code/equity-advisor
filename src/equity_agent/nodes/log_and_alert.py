# ABOUTME: Log and alert node -- terminal action node. Always logs the verdict to the
# ABOUTME: verdicts table; sends an MCP alert only when the verdict is "flag".

import datetime
import sqlite3
from pathlib import Path

from equity_agent.mcp.client import send_alert
from equity_agent.state import AgentState

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "equity_research.db"


def _log_verdict(ticker: str, verdict: str, confidence: float, summary: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO verdicts (ticker, verdict, confidence, summary, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (ticker, verdict, confidence, summary, datetime.date.today().isoformat()),
    )
    conn.commit()
    conn.close()


def log_and_alert_node(state: AgentState) -> dict:
    ticker = state["ticker"]
    verdict = state["verdict"]
    summary = state["aggregated_signal"]["summary"]

    _log_verdict(ticker, verdict, state["confidence"], summary)

    if verdict == "flag":
        send_alert(ticker, summary)

    return {}
