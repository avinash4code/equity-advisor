# ABOUTME: Integration test for fundamentals_analyst_node against a real (temp) SQLite file
# ABOUTME: and a real local Chroma store -- no mocked RAG or DB. Live price is still fetched
# ABOUTME: over MCP/yfinance (real, network-bound), matching the "price is always live" design.

import sqlite3
from pathlib import Path

from langchain_community.embeddings import FakeEmbeddings
from langchain_community.vectorstores import Chroma

import equity_agent.nodes.fundamentals_analyst as fundamentals_analyst
import equity_agent.rag.retriever as retriever
from equity_agent.nodes.fundamentals_analyst import fundamentals_analyst_node
from equity_agent.rag.ingest import ingest_document

SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "src" / "db" / "schema.sql"


def test_fresh_report_flows_through_rag_extraction_to_real_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_equity_research.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA_PATH.read_text())
    conn.close()
    monkeypatch.setattr(fundamentals_analyst, "DB_PATH", db_path)

    chroma_store = Chroma(
        collection_name="equity_docs_integration_test",
        embedding_function=FakeEmbeddings(size=8),
        persist_directory=str(tmp_path / "chroma_test"),
    )
    monkeypatch.setattr(retriever, "_get_vectorstore", lambda: chroma_store)

    ingest_document(
        ticker="TCS.NS",
        doc_type="quarterly_report",
        report_period="2027-Q1",
        report_date="2026-07-15",
        text=(
            "TCS Q1 FY27 Results: Net income Rs 133,490,000,000. "
            "Revenue Rs 722,750,000,000, prior-year quarter revenue Rs 634,370,000,000. "
            "Total equity Rs 1,072,400,000,000. Total debt Rs 112,830,000,000. "
            "Basic EPS Rs 36.90."
        ),
        vectorstore=chroma_store,
    )

    result = fundamentals_analyst_node({"ticker": "TCS.NS"})

    assert result["fundamentals"]["eps"] == 36.9
    assert result["fundamentals"]["pe_ratio"] is not None
    assert result["fundamentals"]["roe"] is not None

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT ticker, as_of_date, eps, roe FROM fundamentals WHERE ticker = ?",
        ("TCS.NS",),
    ).fetchone()
    conn.close()

    assert row == ("TCS.NS", "2026-07-15", 36.9, result["fundamentals"]["roe"])
