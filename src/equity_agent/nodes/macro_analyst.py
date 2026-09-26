# ABOUTME: Macro analyst node -- cache-aware fetch of macroeconomic factors (rates, inflation,
# ABOUTME: currency, policy) relevant to the ticker, via nodes._signal_fetch.

from equity_agent.nodes._signal_fetch import fetch_cache_aware_signal
from equity_agent.state import AgentState

_PROMPT = (
    "Assess the current macroeconomic environment -- interest rates, inflation, "
    "currency, fiscal/monetary policy -- as it bears on the company below."
)


def macro_analyst_node(state: AgentState) -> dict:
    signal = fetch_cache_aware_signal(state["ticker"], "macro", "macro_note", _PROMPT)
    return {"macro_signal": signal}
