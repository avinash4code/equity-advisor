# ABOUTME: Shared LangGraph state definition for the equity research agent.
# ABOUTME: All node modules import AgentState from here, not from graph.py, to avoid circular imports.

from typing import Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    ticker: str
    messages: list[BaseMessage]
    retrieved_docs: list[str]   # populated from v1 onward
    sql_results: dict           # populated from v2 onward
    fundamentals: dict          # populated by fundamentals_analyst node
    live_data: dict             # populated by live_data node (v3, MCP)
    next_step: Optional[str]    # router's decision
    macro_signal: dict          # populated by macro_analyst node
    sector_signal: dict         # populated by sector_analyst node
    competition_signal: dict    # populated by competition_analyst node
    aggregated_signal: dict     # populated by signal_aggregator node
    confidence: float           # populated by signal_aggregator node
    verdict: Literal["flag", "no_action", "need_more_data"]  # populated by trade_analyst node
    in_portfolio: bool          # populated by portfolio_check node
    holding: Optional[dict]     # populated by existing_holding node
    invest_amount: Optional[float]  # populated by new_investment node
    trade_plan: dict            # populated by build_trade_plan node
