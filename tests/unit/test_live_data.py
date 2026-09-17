# ABOUTME: Unit tests for live_data_node against a mocked MCP client -- no real network calls.

from unittest.mock import patch

from equity_agent.nodes.live_data import live_data_node


def test_live_data_node_shapes_state_from_mcp_response():
    fake_financials = {
        "price": 2195.10,
        "shares_outstanding": 3618087518,
        "eps": 36.90,
        "net_income": 133490000000.0,
        "revenue": 722750000000.0,
        "revenue_prior_year": 634370000000.0,
        "total_equity": 1072400000000.0,
        "total_debt": 112830000000.0,
        "as_of_date": "2026-06-30",
    }
    with patch(
        "equity_agent.nodes.live_data.fetch_live_financials", return_value=fake_financials
    ) as mock_fetch:
        result = live_data_node({"ticker": "TCS.NS"})

    mock_fetch.assert_called_once_with("TCS.NS")
    assert result == {"live_data": fake_financials}
