# ABOUTME: Unit tests for fundamentals_analyst_node's RAG-vs-live branching, mocking
# ABOUTME: the retriever, MCP client, LLM extraction, and sqlite -- no real I/O.

import datetime
from unittest.mock import MagicMock, patch

from equity_agent.nodes.fundamentals_analyst import fundamentals_analyst_node

FRESH_DATE = datetime.date.today().isoformat()
STALE_DATE = (datetime.date.today() - datetime.timedelta(days=400)).isoformat()

PRICE_INFO = {"price": 2200.0, "shares_outstanding": 3600000000, "as_of_date": FRESH_DATE}
LIVE_FINANCIALS = {
    "price": 2200.0,
    "shares_outstanding": 3600000000,
    "eps": 36.9,
    "net_income": 133490000000.0,
    "revenue": 722750000000.0,
    "revenue_prior_year": 634370000000.0,
    "total_equity": 1072400000000.0,
    "total_debt": 112830000000.0,
    "as_of_date": FRESH_DATE,
}


def _mocks(report, extracted):
    return {
        "get_latest_quarterly_report": MagicMock(return_value=report),
        "_extract_financials_from_report": MagicMock(return_value=extracted),
        "fetch_live_financials": MagicMock(return_value=LIVE_FINANCIALS),
        "fetch_live_price": MagicMock(return_value=PRICE_INFO),
        "_store_fundamentals": MagicMock(),
    }


def _patched(report, extracted):
    mocks = _mocks(report, extracted)
    return patch.multiple("equity_agent.nodes.fundamentals_analyst", **mocks), mocks


def test_fresh_rag_report_skips_live_financials_pull():
    report = {"text": "report text", "report_period": "2027-Q1", "report_date": FRESH_DATE}
    extracted = {
        "net_income": 100.0, "revenue": 500.0, "revenue_prior_year": 450.0,
        "total_equity": 1000.0, "total_debt": 200.0, "eps": 10.0,
    }
    patcher, mocks = _patched(report, extracted)
    with patcher:
        result = fundamentals_analyst_node({"ticker": "TCS.NS"})

    mocks["_extract_financials_from_report"].assert_called_once_with("report text")
    mocks["fetch_live_financials"].assert_not_called()
    mocks["fetch_live_price"].assert_called_once_with("TCS.NS")
    mocks["_store_fundamentals"].assert_called_once()
    assert result["fundamentals"]["eps"] == 10.0
    assert result["fundamentals"]["pe_ratio"] == 220.0


def test_stale_rag_report_triggers_live_pull():
    report = {"text": "old report", "report_period": "2025-Q1", "report_date": STALE_DATE}
    patcher, mocks = _patched(report, extracted={})
    with patcher:
        result = fundamentals_analyst_node({"ticker": "TCS.NS"})

    mocks["_extract_financials_from_report"].assert_not_called()
    mocks["fetch_live_financials"].assert_called_once_with("TCS.NS")
    assert result["fundamentals"]["eps"] == 36.9


def test_missing_rag_report_triggers_live_pull():
    patcher, mocks = _patched(report=None, extracted={})
    with patcher:
        fundamentals_analyst_node({"ticker": "TCS.NS"})

    mocks["_extract_financials_from_report"].assert_not_called()
    mocks["fetch_live_financials"].assert_called_once_with("TCS.NS")


def test_stores_ratios_with_as_of_date_from_source_used():
    report = {"text": "report text", "report_period": "2027-Q1", "report_date": FRESH_DATE}
    extracted = {
        "net_income": 100.0, "revenue": 500.0, "revenue_prior_year": 450.0,
        "total_equity": 1000.0, "total_debt": 200.0, "eps": 10.0,
    }
    patcher, mocks = _patched(report, extracted)
    with patcher:
        fundamentals_analyst_node({"ticker": "TCS.NS"})

    args, _ = mocks["_store_fundamentals"].call_args
    assert args[0] == "TCS.NS"
    assert args[1] == FRESH_DATE
