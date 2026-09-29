# ABOUTME: Unit tests for get_quarterly_financials' currency normalization and TTM
# ABOUTME: (trailing four quarters) net_income summing / derived eps -- mocks yfinance
# ABOUTME: entirely, no real network calls.

from unittest.mock import MagicMock, patch

import pandas as pd

from equity_agent.mcp.market_data_server import get_quarterly_financials

Q1 = pd.Timestamp("2026-06-30")  # latest
Q2 = pd.Timestamp("2026-03-31")
Q3 = pd.Timestamp("2025-12-31")
Q4 = pd.Timestamp("2025-09-30")
PRIOR_YEAR = pd.Timestamp("2025-06-30")  # same quarter as Q1, one year back

SHARES = 4_050_343_559


def _mock_ticker(financial_currency: str, trading_currency: str = "INR", q4_eps=0.19):
    # Q4's Basic EPS is nullable on purpose: real yfinance data has quarters with a
    # NaN Basic EPS but a present Net Income, which is exactly what eps is derived
    # from Net Income instead of summed from this row.
    quarterly_financials = pd.DataFrame(
        {
            Q1: [0.20, 819_000_000.0, 5_082_000_000.0],
            Q2: [0.23, 890_000_000.0, 5_040_000_000.0],
            Q3: [0.18, 720_000_000.0, 5_099_000_000.0],
            Q4: [q4_eps, 760_000_000.0, 5_076_000_000.0],
            PRIOR_YEAR: [0.20, 780_000_000.0, 4_941_000_000.0],
        },
        index=["Basic EPS", "Net Income", "Total Revenue"],
    )
    quarterly_balance_sheet = pd.DataFrame(
        {Q1: [9_619_000_000.0, 923_000_000.0]},
        index=["Stockholders Equity", "Total Debt"],
    )

    mock_t = MagicMock()
    mock_t.fast_info.currency = trading_currency
    mock_t.fast_info.last_price = 1015.4
    mock_t.fast_info.shares = SHARES
    mock_t.info = {"financialCurrency": financial_currency}
    mock_t.quarterly_financials = quarterly_financials
    mock_t.quarterly_balance_sheet = quarterly_balance_sheet
    return mock_t


def test_converts_ttm_usd_financials_to_trading_currency():
    fx_rate = 96.0
    mock_infy = _mock_ticker(financial_currency="USD", trading_currency="INR")
    mock_fx = MagicMock()
    mock_fx.fast_info.last_price = fx_rate

    def ticker_side_effect(symbol):
        return mock_fx if symbol == "USDINR=X" else mock_infy

    with patch("equity_agent.mcp.market_data_server.yf.Ticker", side_effect=ticker_side_effect):
        result = get_quarterly_financials("INFY.NS")

    ttm_net_income = (819_000_000.0 + 890_000_000.0 + 720_000_000.0 + 760_000_000.0) * fx_rate
    assert result["price"] == 1015.4  # price is already in trading currency, untouched
    assert result["net_income"] == ttm_net_income
    assert result["eps"] == ttm_net_income / SHARES
    assert result["revenue"] == 5_082_000_000.0 * fx_rate  # single latest quarter, not TTM
    assert result["revenue_prior_year"] == 4_941_000_000.0 * fx_rate
    assert result["total_equity"] == 9_619_000_000.0 * fx_rate
    assert result["total_debt"] == 923_000_000.0 * fx_rate


def test_no_conversion_when_currencies_match():
    mock_t = _mock_ticker(financial_currency="INR", trading_currency="INR")

    with patch("equity_agent.mcp.market_data_server.yf.Ticker", return_value=mock_t) as mock_ticker:
        result = get_quarterly_financials("SOMENSE.NS")

    mock_ticker.assert_called_once_with("SOMENSE.NS")  # no extra FX-ticker lookup
    ttm_net_income = 819_000_000.0 + 890_000_000.0 + 720_000_000.0 + 760_000_000.0
    assert result["net_income"] == ttm_net_income
    assert result["eps"] == ttm_net_income / SHARES


def test_eps_is_derived_from_net_income_not_summed_from_a_gappy_basic_eps_row():
    mock_t = _mock_ticker(financial_currency="INR", trading_currency="INR", q4_eps=float("nan"))

    with patch("equity_agent.mcp.market_data_server.yf.Ticker", return_value=mock_t):
        result = get_quarterly_financials("SOMENSE.NS")

    # Q4's Basic EPS is NaN but its Net Income (760M) is present, so a naive sum of
    # the Basic EPS row would undercount -- eps must come from net_income / shares.
    ttm_net_income = 819_000_000.0 + 890_000_000.0 + 720_000_000.0 + 760_000_000.0
    assert result["net_income"] == ttm_net_income
    assert result["eps"] == ttm_net_income / SHARES


def test_ttm_sums_fewer_than_four_quarters_when_that_is_all_thats_available():
    mock_t = _mock_ticker(financial_currency="INR", trading_currency="INR")
    mock_t.quarterly_financials = mock_t.quarterly_financials[[Q1, Q2]]

    with patch("equity_agent.mcp.market_data_server.yf.Ticker", return_value=mock_t):
        result = get_quarterly_financials("SOMENSE.NS")

    ttm_net_income = 819_000_000.0 + 890_000_000.0
    assert result["net_income"] == ttm_net_income
    assert result["eps"] == ttm_net_income / SHARES
