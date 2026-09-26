# ABOUTME: Shared cache-aware fetch logic for the macro/sector/competition analyst nodes:
# ABOUTME: reuse a fresh cached signal, else RAG-synthesize from the latest indexed doc, else LLM-only.

import datetime
import sqlite3
from pathlib import Path

from pydantic import BaseModel

from equity_agent.config import STALE_AFTER_DAYS
from equity_agent.llm import llm
from equity_agent.rag.retriever import get_latest_document

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "equity_research.db"


class _Signal(BaseModel):
    summary: str
    score: float | None
    confidence: float


def _is_stale(as_of_date: str, max_age_days: int = STALE_AFTER_DAYS) -> bool:
    age = datetime.date.today() - datetime.date.fromisoformat(as_of_date)
    return age.days > max_age_days


def _get_cached_signal(ticker: str, kind: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT summary, score, confidence, as_of_date FROM signals "
        "WHERE ticker = ? AND kind = ? ORDER BY as_of_date DESC LIMIT 1",
        (ticker, kind),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return {"summary": row[0], "score": row[1], "confidence": row[2], "as_of_date": row[3]}


def _synthesize_from_doc(text: str, prompt: str) -> dict:
    # method="json_mode": matches fundamentals_analyst's workaround for the deepseek-backed LLM.
    synthesizer = llm.with_structured_output(_Signal, method="json_mode")
    result = synthesizer.invoke(
        f"{prompt} Respond with a JSON object with exactly these keys: summary, score "
        f"(-1..1 direction/strength, or null if not applicable), confidence (0..1).\n\n{text}"
    )
    return result.model_dump()


def _synthesize_from_context(ticker: str, prompt: str) -> dict:
    synthesizer = llm.with_structured_output(_Signal, method="json_mode")
    result = synthesizer.invoke(
        f"{prompt} Respond with a JSON object with exactly these keys: summary, score "
        "(-1..1 direction/strength, or null if not applicable), confidence (0..1).\n\n"
        f"No indexed document is available for {ticker}. Reason from general knowledge "
        "and keep confidence low to reflect the lack of a grounded source."
    )
    return result.model_dump()


def _store_signal(ticker: str, kind: str, as_of_date: str, signal: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO signals (ticker, kind, as_of_date, summary, score, confidence) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (ticker, kind, as_of_date, signal["summary"], signal["score"], signal["confidence"]),
    )
    conn.commit()
    conn.close()


def fetch_cache_aware_signal(ticker: str, kind: str, doc_type: str, prompt: str) -> dict:
    """Returns {"summary", "score", "confidence"} for (ticker, kind), from cache/RAG/LLM."""
    cached = _get_cached_signal(ticker, kind)
    if cached is not None and not _is_stale(cached["as_of_date"]):
        return {"summary": cached["summary"], "score": cached["score"], "confidence": cached["confidence"]}

    doc = get_latest_document(ticker, doc_type)
    if doc is not None:
        signal = _synthesize_from_doc(doc["text"], prompt)
        as_of_date = doc["report_date"]
    else:
        signal = _synthesize_from_context(ticker, prompt)
        as_of_date = datetime.date.today().isoformat()

    _store_signal(ticker, kind, as_of_date, signal)
    return signal
