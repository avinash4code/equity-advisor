# ABOUTME: Unit tests for get_latest_quarterly_report against a mocked Chroma vectorstore.

from unittest.mock import MagicMock

from equity_agent.rag.retriever import get_latest_quarterly_report


def _mock_store(matches: dict) -> MagicMock:
    store = MagicMock()
    store.get.return_value = matches
    return store


def test_returns_none_when_no_docs_indexed():
    store = _mock_store({"ids": [], "documents": [], "metadatas": []})
    assert get_latest_quarterly_report("TCS.NS", vectorstore=store) is None


def test_picks_doc_with_max_report_date():
    store = _mock_store(
        {
            "ids": ["a", "b"],
            "documents": ["older report text", "newer report text"],
            "metadatas": [
                {"ticker": "TCS.NS", "doc_type": "quarterly_report",
                 "report_period": "2026-Q1", "report_date": "2026-01-15"},
                {"ticker": "TCS.NS", "doc_type": "quarterly_report",
                 "report_period": "2026-Q2", "report_date": "2026-07-15"},
            ],
        }
    )
    result = get_latest_quarterly_report("TCS.NS", vectorstore=store)
    assert result == {
        "text": "newer report text",
        "report_period": "2026-Q2",
        "report_date": "2026-07-15",
    }


def test_filters_on_ticker_and_doc_type():
    store = _mock_store({"ids": [], "documents": [], "metadatas": []})
    get_latest_quarterly_report("TCS.NS", vectorstore=store)
    where_arg = store.get.call_args.kwargs["where"]
    assert {"ticker": {"$eq": "TCS.NS"}} in where_arg["$and"]
    assert {"doc_type": {"$eq": "quarterly_report"}} in where_arg["$and"]
