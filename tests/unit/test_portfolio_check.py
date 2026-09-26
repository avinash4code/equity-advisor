# ABOUTME: Unit tests for portfolio_check_node -- mocks the DB lookup, no real sqlite I/O.

from unittest.mock import MagicMock, patch

from equity_agent.nodes.portfolio_check import portfolio_check_node


def test_ticker_in_portfolio():
    with patch("equity_agent.nodes.portfolio_check._is_in_portfolio", MagicMock(return_value=True)):
        result = portfolio_check_node({"ticker": "TCS.NS"})
    assert result == {"in_portfolio": True}


def test_ticker_not_in_portfolio():
    with patch("equity_agent.nodes.portfolio_check._is_in_portfolio", MagicMock(return_value=False)):
        result = portfolio_check_node({"ticker": "INFY.NS"})
    assert result == {"in_portfolio": False}
