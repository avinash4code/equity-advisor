# ABOUTME: Unit tests for fetch_cache_aware_signal's cache/RAG/LLM-fallback branching,
# ABOUTME: mocking sqlite, the retriever, and the LLM -- no real I/O.

import datetime
from unittest.mock import MagicMock, patch

from equity_agent.nodes._signal_fetch import fetch_cache_aware_signal

FRESH_DATE = datetime.date.today().isoformat()
STALE_DATE = (datetime.date.today() - datetime.timedelta(days=400)).isoformat()

DOC = {"text": "macro note text", "report_period": "2026-Q2", "report_date": FRESH_DATE}
SYNTHESIZED = {"summary": "Rate cuts likely, tailwind for financing costs.", "score": 0.4, "confidence": 0.7}


def _mocks(cached, doc):
    return {
        "_get_cached_signal": MagicMock(return_value=cached),
        "get_latest_document": MagicMock(return_value=doc),
        "_synthesize_from_doc": MagicMock(return_value=SYNTHESIZED),
        "_synthesize_from_context": MagicMock(return_value=SYNTHESIZED),
        "_store_signal": MagicMock(),
    }


def _patched(cached, doc):
    mocks = _mocks(cached, doc)
    return patch.multiple("equity_agent.nodes._signal_fetch", **mocks), mocks


def test_fresh_cache_hit_skips_rag_and_llm():
    cached = {"summary": "cached", "score": 0.1, "confidence": 0.6, "as_of_date": FRESH_DATE}
    patcher, mocks = _patched(cached, doc=None)
    with patcher:
        result = fetch_cache_aware_signal("TCS.NS", "macro", "macro_note", "prompt")

    mocks["get_latest_document"].assert_not_called()
    mocks["_synthesize_from_doc"].assert_not_called()
    mocks["_store_signal"].assert_not_called()
    assert result == {"summary": "cached", "score": 0.1, "confidence": 0.6}


def test_stale_cache_with_doc_synthesizes_from_doc_and_stores():
    cached = {"summary": "old", "score": 0.0, "confidence": 0.5, "as_of_date": STALE_DATE}
    patcher, mocks = _patched(cached, doc=DOC)
    with patcher:
        result = fetch_cache_aware_signal("TCS.NS", "macro", "macro_note", "prompt")

    mocks["get_latest_document"].assert_called_once_with("TCS.NS", "macro_note")
    mocks["_synthesize_from_doc"].assert_called_once_with("macro note text", "prompt")
    mocks["_synthesize_from_context"].assert_not_called()
    mocks["_store_signal"].assert_called_once_with("TCS.NS", "macro", FRESH_DATE, SYNTHESIZED)
    assert result == SYNTHESIZED


def test_missing_cache_and_missing_doc_falls_back_to_llm_only():
    patcher, mocks = _patched(cached=None, doc=None)
    with patcher:
        result = fetch_cache_aware_signal("TCS.NS", "sector", "sector_report", "prompt")

    mocks["_synthesize_from_doc"].assert_not_called()
    mocks["_synthesize_from_context"].assert_called_once_with("TCS.NS", "prompt")
    mocks["_store_signal"].assert_called_once()
    assert result == SYNTHESIZED


def test_missing_cache_with_doc_synthesizes_from_doc():
    patcher, mocks = _patched(cached=None, doc=DOC)
    with patcher:
        fetch_cache_aware_signal("TCS.NS", "competition", "competitor_analysis", "prompt")

    mocks["_synthesize_from_doc"].assert_called_once_with("macro note text", "prompt")
    mocks["_synthesize_from_context"].assert_not_called()
