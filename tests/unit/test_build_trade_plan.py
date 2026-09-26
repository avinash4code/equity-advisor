# ABOUTME: Unit tests for build_trade_plan_node -- pure function, table-driven, no mocking.

from equity_agent.nodes.build_trade_plan import build_trade_plan_node


def test_sizes_by_existing_holding_quantity_and_sets_stop_loss_on_add():
    state = {
        "trade_decision": {"action": "add", "verdict": "flag", "rationale": "Strong fundamentals."},
        "holding": {"quantity": 10, "avg_price": 3850.0},
        "invest_amount": None,
    }
    result = build_trade_plan_node(state)
    assert result == {
        "trade_plan": {
            "action": "add",
            "quantity": 10,
            "stop_loss_pct": -0.08,
            "trigger_conditions": ["Strong fundamentals."],
        }
    }


def test_sizes_by_invest_amount_when_not_held():
    state = {
        "trade_decision": {"action": "buy", "verdict": "flag", "rationale": "New position."},
        "holding": None,
        "invest_amount": 50000.0,
    }
    result = build_trade_plan_node(state)
    assert result["trade_plan"]["amount"] == 50000.0
    assert result["trade_plan"]["stop_loss_pct"] == -0.08


def test_no_stop_loss_on_exit_actions():
    state = {
        "trade_decision": {"action": "trim", "verdict": "no_action", "rationale": "Take some profit."},
        "holding": {"quantity": 10, "avg_price": 3850.0},
        "invest_amount": None,
    }
    result = build_trade_plan_node(state)
    assert result["trade_plan"]["stop_loss_pct"] is None
