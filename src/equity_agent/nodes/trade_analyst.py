# ABOUTME: Trade analyst node -- turns the aggregated signal plus position context
# ABOUTME: (existing holding or invest amount) into a buy/sell/hold decision and verdict.

from typing import Literal

from pydantic import BaseModel

from equity_agent.llm import llm
from equity_agent.state import AgentState


class _TradeDecision(BaseModel):
    action: Literal["buy", "sell", "hold", "add", "trim"]
    verdict: Literal["flag", "no_action", "need_more_data"]
    rationale: str


def trade_analyst_node(state: AgentState) -> dict:
    position = (
        f"Existing holding: {state['holding']}"
        if state.get("holding") is not None
        else f"Not currently held. Amount available to invest: {state.get('invest_amount')}"
    )
    prompt = (
        "Given the aggregated research signal and current position below, decide a trade "
        "action. Respond with a JSON object with exactly these keys: action "
        "(buy/sell/hold/add/trim), verdict (flag/no_action/need_more_data), rationale.\n\n"
        f"Aggregated signal: {state.get('aggregated_signal')}\n"
        f"Confidence: {state.get('confidence')}\n"
        f"{position}"
    )
    # method="json_mode": matches fundamentals_analyst's workaround for the deepseek-backed LLM.
    decider = llm.with_structured_output(_TradeDecision, method="json_mode")
    decision = decider.invoke(prompt).model_dump()
    return {"trade_decision": decision, "verdict": decision["verdict"]}
