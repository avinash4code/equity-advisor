# ABOUTME: Existing holding node -- reads the ticker's current lots from the portfolio
# ABOUTME: table (RDBMS) and aggregates them into a single weighted position.

import sqlite3
from pathlib import Path

from equity_agent.state import AgentState

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "equity_research.db"


def _fetch_lots(ticker: str) -> list[tuple[float, float]]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT quantity, avg_price FROM portfolio WHERE ticker = ?", (ticker,)
    ).fetchall()
    conn.close()
    return rows


def _aggregate_lots(rows: list[tuple[float, float]]) -> dict:
    """Pure function: per-lot (quantity, avg_price) rows -> one weighted position."""
    total_quantity = sum(quantity for quantity, _ in rows)
    weighted_cost = sum(quantity * avg_price for quantity, avg_price in rows)
    return {
        "quantity": total_quantity,
        "avg_price": weighted_cost / total_quantity if total_quantity else 0.0,
    }


def existing_holding_node(state: AgentState) -> dict:
    return {"holding": _aggregate_lots(_fetch_lots(state["ticker"]))}
