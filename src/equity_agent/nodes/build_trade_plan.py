# ABOUTME: Build trade plan node -- deterministic mapping from the trade_analyst decision
# ABOUTME: and position context into a concrete plan (sizing, stop-loss, trigger).

from equity_agent.state import AgentState

STOP_LOSS_PCT = -0.08  # flat heuristic; no live price is carried in state to size off yet

_ENTRY_ACTIONS = {"buy", "add"}


def _size_trade(decision: dict, holding: dict | None, invest_amount: float | None) -> dict:
    if holding is not None:
        return {"quantity": holding["quantity"]}
    return {"amount": invest_amount}


def build_trade_plan_node(state: AgentState) -> dict:
    decision = state["trade_decision"]
    sizing = _size_trade(decision, state.get("holding"), state.get("invest_amount"))

    trade_plan = {
        "action": decision["action"],
        **sizing,
        "stop_loss_pct": STOP_LOSS_PCT if decision["action"] in _ENTRY_ACTIONS else None,
        "trigger_conditions": [decision["rationale"]],
    }
    return {"trade_plan": trade_plan}
