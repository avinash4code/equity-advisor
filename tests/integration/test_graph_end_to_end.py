# ABOUTME: Integration test for the full graph against a real (temp) SQLite file and a real
# ABOUTME: local Chroma store -- LLM (deepseek), yfinance, and MCP alert calls are all real.

import sqlite3
from pathlib import Path

from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma

import equity_agent.nodes._signal_fetch as signal_fetch
import equity_agent.nodes.existing_holding as existing_holding
import equity_agent.nodes.fundamentals_analyst as fundamentals_analyst
import equity_agent.nodes.log_and_alert as log_and_alert
import equity_agent.nodes.portfolio_check as portfolio_check
import equity_agent.rag.retriever as retriever
from equity_agent.graph import app

SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "src" / "db" / "schema.sql"


def test_full_graph_run_produces_trade_plan_and_logs_verdict(tmp_path, monkeypatch):
    db_path = tmp_path / "test_equity_research.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.execute(
        "INSERT INTO portfolio (ticker, quantity, avg_price, bought_at) VALUES (?, ?, ?, ?)",
        ("TCS.NS", 10, 3850.0, "2025-03-10"),
    )
    conn.commit()
    conn.close()

    for module in (fundamentals_analyst, signal_fetch, portfolio_check, existing_holding, log_and_alert):
        monkeypatch.setattr(module, "DB_PATH", db_path)

    chroma_store = Chroma(
        collection_name="equity_docs_graph_integration_test",
        embedding_function=FakeEmbeddings(size=8),
        persist_directory=str(tmp_path / "chroma_test"),
    )
    monkeypatch.setattr(retriever, "_get_vectorstore", lambda: chroma_store)

    result = app.invoke({"ticker": "TCS.NS", "messages": []})

    assert result["verdict"] in ("flag", "no_action", "need_more_data")
    assert result["trade_plan"]["action"] in ("buy", "sell", "hold", "add", "trim")
    assert result["holding"] == {"quantity": 10, "avg_price": 3850.0}

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT ticker, verdict FROM verdicts WHERE ticker = ?", ("TCS.NS",)
    ).fetchone()
    conn.close()
    assert row == ("TCS.NS", result["verdict"])
