# ABOUTME: Unit test for new_investment_node -- returns the configured placeholder amount.

from equity_agent.config import DEFAULT_INVEST_AMOUNT
from equity_agent.nodes.new_investment import new_investment_node


def test_returns_default_invest_amount():
    assert new_investment_node({"ticker": "INFY.NS"}) == {"invest_amount": DEFAULT_INVEST_AMOUNT}
