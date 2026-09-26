# ABOUTME: Portfolio check node -- cheap existence check for whether the ticker is
# ABOUTME: already held, deciding the existing_holding/new_investment branch.

import sqlite3
from pathlib import Path

from equity_agent.state import AgentState

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "equity_research.db"


def _is_in_portfolio(ticker: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT 1 FROM portfolio WHERE ticker = ? LIMIT 1", (ticker,)).fetchone()
    conn.close()
    return row is not None


def portfolio_check_node(state: AgentState) -> dict:
    return {"in_portfolio": _is_in_portfolio(state["ticker"])}
