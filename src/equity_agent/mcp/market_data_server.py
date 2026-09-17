# ABOUTME: MCP server exposing live quarterly financials (yfinance-backed) as a single tool.
# ABOUTME: Run standalone for manual testing; normally spawned over stdio by mcp/client.py.

import datetime

import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("market-data")


@mcp.tool()
def get_quarterly_financials(ticker: str) -> dict:
    """Latest-quarter raw financials for `ticker` from yfinance.

    Returns price, shares_outstanding, eps, net_income, revenue,
    revenue_prior_year (same quarter, one year back, or None if unavailable),
    total_equity, total_debt (None if unavailable), and as_of_date (ISO date
    of the latest quarter end).
    """
    t = yf.Ticker(ticker)
    quarterly_financials = t.quarterly_financials
    quarterly_balance_sheet = t.quarterly_balance_sheet

    latest_date = quarterly_financials.columns[0]
    prior_year_date = latest_date - datetime.timedelta(days=365)
    prior_year_cols = [
        c for c in quarterly_financials.columns
        if abs((c - prior_year_date).days) <= 15
    ]
    revenue_prior_year = (
        float(quarterly_financials.loc["Total Revenue", prior_year_cols[0]])
        if prior_year_cols
        else None
    )

    # The balance sheet snapshot typically lags the income statement by one
    # quarter on yfinance, so use the most recent balance-sheet column
    # available rather than requiring an exact match with latest_date.
    total_equity = None
    total_debt = None
    if len(quarterly_balance_sheet.columns) > 0:
        latest_balance_date = quarterly_balance_sheet.columns[0]
        if "Stockholders Equity" in quarterly_balance_sheet.index:
            total_equity = float(
                quarterly_balance_sheet.loc["Stockholders Equity", latest_balance_date]
            )
        if "Total Debt" in quarterly_balance_sheet.index:
            total_debt = float(
                quarterly_balance_sheet.loc["Total Debt", latest_balance_date]
            )

    return {
        "price": t.fast_info.last_price,
        "shares_outstanding": t.fast_info.shares,
        "eps": float(quarterly_financials.loc["Basic EPS", latest_date]),
        "net_income": float(quarterly_financials.loc["Net Income", latest_date]),
        "revenue": float(quarterly_financials.loc["Total Revenue", latest_date]),
        "revenue_prior_year": revenue_prior_year,
        "total_equity": total_equity,
        "total_debt": total_debt,
        "as_of_date": latest_date.date().isoformat(),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
