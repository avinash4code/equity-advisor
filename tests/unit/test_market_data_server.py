# ABOUTME: Unit tests for get_quarterly_financials' currency normalization -- mocks
# ABOUTME: yfinance entirely, no real network calls.

from unittest.mock import MagicMock, patch

import pandas as pd

from equity_agent.mcp.market_data_server import get_quarterly_financials

LATEST = pd.Timestamp("2026-06-30")
PRIOR_YEAR = pd.Timestamp("2025-06-30")


def _mock_ticker(financial_currency: str, trading_currency: str = "INR"):
    quarterly_financials = pd.DataFrame(
        {LATEST: [0.20, 819_000_000.0, 5_082_000_000.0], PRIOR_YEAR: [0.18, 780_000_000.0, 4_941_000_000.0]},
        index=["Basic EPS", "Net Income", "Total Revenue"],
    )
    quarterly_balance_sheet = pd.DataFrame(
        {LATEST: [9_619_000_000.0, 923_000_000.0]},
        index=["Stockholders Equity", "Total Debt"],
    )

    mock_t = MagicMock()
    mock_t.fast_info.currency = trading_currency
    mock_t.fast_info.last_price = 1015.4
    mock_t.fast_info.shares = 4_050_343_559
    mock_t.info = {"financialCurrency": financial_currency}
    mock_t.quarterly_financials = quarterly_financials
    mock_t.quarterly_balance_sheet = quarterly_balance_sheet
    return mock_t


def test_converts_usd_financials_to_trading_currency():
    fx_rate = 96.0
    mock_infy = _mock_ticker(financial_currency="USD", trading_currency="INR")
    mock_fx = MagicMock()
    mock_fx.fast_info.last_price = fx_rate

    def ticker_side_effect(symbol):
        return mock_fx if symbol == "USDINR=X" else mock_infy

    with patch("equity_agent.mcp.market_data_server.yf.Ticker", side_effect=ticker_side_effect):
        result = get_quarterly_financials("INFY.NS")

    assert result["price"] == 1015.4  # price is already in trading currency, untouched
    assert result["eps"] == 0.20 * fx_rate
    assert result["net_income"] == 819_000_000.0 * fx_rate
    assert result["revenue"] == 5_082_000_000.0 * fx_rate
    assert result["revenue_prior_year"] == 4_941_000_000.0 * fx_rate
    assert result["total_equity"] == 9_619_000_000.0 * fx_rate
    assert result["total_debt"] == 923_000_000.0 * fx_rate


def test_no_conversion_when_currencies_match():
    mock_t = _mock_ticker(financial_currency="INR", trading_currency="INR")

    with patch("equity_agent.mcp.market_data_server.yf.Ticker", return_value=mock_t) as mock_ticker:
        result = get_quarterly_financials("SOMENSE.NS")

    mock_ticker.assert_called_once_with("SOMENSE.NS")  # no extra FX-ticker lookup
    assert result["eps"] == 0.20
    assert result["net_income"] == 819_000_000.0
