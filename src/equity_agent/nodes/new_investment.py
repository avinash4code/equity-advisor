# ABOUTME: New investment node -- amount to consider investing when the ticker isn't
# ABOUTME: already held. Placeholder until a real cash/budget source exists.

from equity_agent.config import DEFAULT_INVEST_AMOUNT
from equity_agent.state import AgentState


def new_investment_node(state: AgentState) -> dict:
    return {"invest_amount": DEFAULT_INVEST_AMOUNT}
