# ABOUTME: Shared LangGraph state definition for the equity research agent.
# ABOUTME: All node modules import AgentState from here, not from graph.py, to avoid circular imports.

from typing import TypedDict, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    ticker: str
    messages: list[BaseMessage]
    retrieved_docs: list[str]   # populated from v1 onward
    sql_results: dict           # populated from v2 onward
    fundamentals: dict          # populated by fundamentals_analyst node
    live_data: dict             # populated by live_data node (v3, MCP)
    next_step: Optional[str]    # router's decision
