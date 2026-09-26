# ABOUTME: Sector analyst node -- cache-aware fetch of sector-level trends and dynamics
# ABOUTME: relevant to the ticker, via nodes._signal_fetch.

from equity_agent.nodes._signal_fetch import fetch_cache_aware_signal
from equity_agent.state import AgentState

_PROMPT = (
    "Assess the current trends and dynamics in this company's sector -- demand, "
    "capacity, pricing power, regulation -- as they bear on the company below."
)


def sector_analyst_node(state: AgentState) -> dict:
    signal = fetch_cache_aware_signal(state["ticker"], "sector", "sector_report", _PROMPT)
    return {"sector_signal": signal}
