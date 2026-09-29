# ABOUTME: MCP server exposing live quarterly financials (yfinance-backed) as a single tool.
# ABOUTME: Run standalone for manual testing; normally spawned over stdio by mcp/client.py.

import datetime

import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("market-data")


def _fx_rate(from_currency: str, to_currency: str) -> float:
    """Latest from_currency->to_currency rate, or 1.0 if they're the same currency."""
    if from_currency == to_currency:
        return 1.0
    return yf.Ticker(f"{from_currency}{to_currency}=X").fast_info.last_price


@mcp.tool()
def get_quarterly_financials(ticker: str) -> dict:
    """Trailing-twelve-month financials for `ticker` from yfinance, as of the latest quarter.

    Returns price, shares_outstanding, net_income (summed over the trailing
    four reported quarters, or fewer if fewer are available -- this is what
    pe_ratio/roe are conventionally computed against, not a single quarter's
    figure), eps (net_income / shares_outstanding, not yfinance's own "Basic
    EPS" row summed -- that row has had quarters with a NaN EPS but a present
    Net Income, which silently undercounts a naive EPS sum), revenue,
    revenue_prior_year (single-quarter, same
    quarter one year back, or None if unavailable -- QoQ-YoY growth is its
    own convention, not TTM), total_equity, total_debt (latest balance-sheet
    snapshot, None if unavailable), and as_of_date (ISO date of the latest
    quarter end the TTM window ends at).

    yfinance reports quarterly_financials/quarterly_balance_sheet in the
    company's financialCurrency, which for dual-currency tickers (e.g. an
    NSE-listed, USD-reporting company) differs from fast_info's trading
    currency that `price` is quoted in. Converting here keeps every returned
    figure in the ticker's trading currency, so ratios computed downstream
    (like price / eps) aren't accidentally mixing currencies.
    """
    t = yf.Ticker(ticker)
    quarterly_financials = t.quarterly_financials
    quarterly_balance_sheet = t.quarterly_balance_sheet

    trading_currency = t.fast_info.currency
    financial_currency = t.info.get("financialCurrency", trading_currency)
    fx_rate = _fx_rate(financial_currency, trading_currency)

    latest_date = quarterly_financials.columns[0]
    trailing_cols = quarterly_financials.columns[:4]
    prior_year_date = latest_date - datetime.timedelta(days=365)
    prior_year_cols = [
        c for c in quarterly_financials.columns
        if abs((c - prior_year_date).days) <= 15
    ]
    revenue_prior_year = (
        float(quarterly_financials.loc["Total Revenue", prior_year_cols[0]]) * fx_rate
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
            ) * fx_rate
        if "Total Debt" in quarterly_balance_sheet.index:
            total_debt = float(
                quarterly_balance_sheet.loc["Total Debt", latest_balance_date]
            ) * fx_rate

    # .sum() skips NaN quarters (e.g. a missing filing) by default.
    shares_outstanding = t.fast_info.shares
    ttm_net_income = float(quarterly_financials.loc["Net Income", trailing_cols].sum()) * fx_rate
    ttm_eps = ttm_net_income / shares_outstanding

    return {
        "price": t.fast_info.last_price,
        "shares_outstanding": shares_outstanding,
        "eps": ttm_eps,
        "net_income": ttm_net_income,
        "revenue": float(quarterly_financials.loc["Total Revenue", latest_date]) * fx_rate,
        "revenue_prior_year": revenue_prior_year,
        "total_equity": total_equity,
        "total_debt": total_debt,
        "as_of_date": latest_date.date().isoformat(),
    }


@mcp.tool()
def get_price(ticker: str) -> dict:
    """Current price and shares outstanding for `ticker` -- independent of report freshness."""
    t = yf.Ticker(ticker)
    return {
        "price": t.fast_info.last_price,
        "shares_outstanding": t.fast_info.shares,
        "as_of_date": datetime.date.today().isoformat(),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
