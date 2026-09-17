# ABOUTME: RAG-first, live-fallback fundamentals ratio pipeline: checks the latest indexed
# ABOUTME: quarterly report, pulls live financials if it's missing/stale, computes ratios, stores them.

import datetime
import sqlite3
from pathlib import Path

from pydantic import BaseModel

from equity_agent.llm import llm
from equity_agent.mcp.client import fetch_live_financials, fetch_live_price
from equity_agent.rag.retriever import get_latest_quarterly_report
from equity_agent.state import AgentState

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "equity_research.db"
STALE_AFTER_DAYS = 100


class _ExtractedFinancials(BaseModel):
    net_income: float
    revenue: float
    revenue_prior_year: float | None
    total_equity: float | None
    total_debt: float | None
    eps: float


def _is_stale(report_date: str, max_age_days: int = STALE_AFTER_DAYS) -> bool:
    age = datetime.date.today() - datetime.date.fromisoformat(report_date)
    return age.days > max_age_days


def _extract_financials_from_report(text: str) -> dict:
    """Pulls the raw line items a quarterly report never states as ratios."""
    extractor = llm.with_structured_output(_ExtractedFinancials)
    result = extractor.invoke(
        f"Extract net income, revenue, prior-year revenue (same quarter, if stated), "
        f"total equity, total debt, and basic EPS from this quarterly report. "
        f"Use null for any figure not stated.\n\n{text}"
    )
    return result.model_dump()


def _compute_ratios(raw: dict) -> dict:
    """Pure function: raw financials (from RAG extraction or live pull) -> ratios.

    Missing inputs produce a None ratio rather than raising -- a report or live
    pull can legitimately omit a line item (e.g. no prior-year revenue stated).
    """
    price = raw.get("price")
    shares_outstanding = raw.get("shares_outstanding")
    eps = raw.get("eps")
    net_income = raw.get("net_income")
    revenue = raw.get("revenue")
    revenue_prior_year = raw.get("revenue_prior_year")
    total_equity = raw.get("total_equity")
    total_debt = raw.get("total_debt")

    return {
        "pe_ratio": price / eps if price is not None and eps else None,
        "eps": eps,
        "market_cap": price * shares_outstanding if price is not None and shares_outstanding else None,
        "roe": net_income / total_equity if net_income is not None and total_equity else None,
        "debt_to_equity": total_debt / total_equity if total_debt is not None and total_equity else None,
        "revenue_growth_yoy": (
            (revenue / revenue_prior_year) - 1
            if revenue is not None and revenue_prior_year
            else None
        ),
    }


def _store_fundamentals(ticker: str, as_of_date: str, ratios: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO fundamentals "
        "(ticker, as_of_date, pe_ratio, eps, market_cap, roe, debt_to_equity, revenue_growth_yoy) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            ticker,
            as_of_date,
            ratios["pe_ratio"],
            ratios["eps"],
            ratios["market_cap"],
            ratios["roe"],
            ratios["debt_to_equity"],
            ratios["revenue_growth_yoy"],
        ),
    )
    conn.commit()
    conn.close()


def fundamentals_analyst_node(state: AgentState) -> dict:
    ticker = state["ticker"]
    report = get_latest_quarterly_report(ticker)

    if report is not None and not _is_stale(report["report_date"]):
        raw = _extract_financials_from_report(report["text"])
        as_of_date = report["report_date"]
    else:
        raw = fetch_live_financials(ticker)
        as_of_date = raw["as_of_date"]

    price_info = fetch_live_price(ticker)
    raw["price"] = price_info["price"]
    raw["shares_outstanding"] = price_info["shares_outstanding"]

    ratios = _compute_ratios(raw)
    _store_fundamentals(ticker, as_of_date, ratios)
    return {"fundamentals": ratios}
