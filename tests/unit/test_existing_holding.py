# ABOUTME: Unit tests for existing_holding_node -- mocks the DB read, plus pure-function
# ABOUTME: tests for the weighted-average lot aggregation.

from unittest.mock import MagicMock, patch

from equity_agent.nodes.existing_holding import _aggregate_lots, existing_holding_node


def test_node_aggregates_lots_fetched_for_ticker():
    with patch(
        "equity_agent.nodes.existing_holding._fetch_lots",
        MagicMock(return_value=[(10, 3850.0), (5, 4000.0)]),
    ) as mock_fetch:
        result = existing_holding_node({"ticker": "TCS.NS"})

    mock_fetch.assert_called_once_with("TCS.NS")
    assert result == {"holding": {"quantity": 15, "avg_price": (10 * 3850.0 + 5 * 4000.0) / 15}}


def test_aggregate_single_lot():
    assert _aggregate_lots([(10, 3850.0)]) == {"quantity": 10, "avg_price": 3850.0}


def test_aggregate_no_lots_is_zero_not_division_error():
    assert _aggregate_lots([]) == {"quantity": 0, "avg_price": 0.0}
