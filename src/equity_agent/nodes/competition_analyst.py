# ABOUTME: Competition analyst node -- cache-aware fetch of the ticker's competitive
# ABOUTME: positioning relative to peers, via nodes._signal_fetch.

from equity_agent.nodes._signal_fetch import fetch_cache_aware_signal
from equity_agent.state import AgentState

_PROMPT = (
    "Assess this company's competitive positioning relative to its peers -- market "
    "share trends, pricing power, moat -- as it bears on the company below."
)


def competition_analyst_node(state: AgentState) -> dict:
    signal = fetch_cache_aware_signal(state["ticker"], "competition", "competitor_analysis", _PROMPT)
    return {"competition_signal": signal}
