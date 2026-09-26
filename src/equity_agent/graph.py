"""
LangGraph: Indian equity research co-pilot.

START fans out to four parallel analysts (fundamentals, macro, sector,
competition), which join into signal_aggregator. A portfolio-membership
check then branches into existing_holding or new_investment, both of
which converge into trade_analyst -> build_trade_plan -> log_and_alert.
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from equity_agent.nodes.build_trade_plan import build_trade_plan_node
from equity_agent.nodes.competition_analyst import competition_analyst_node
from equity_agent.nodes.existing_holding import existing_holding_node
from equity_agent.nodes.fundamentals_analyst import fundamentals_analyst_node
from equity_agent.nodes.log_and_alert import log_and_alert_node
from equity_agent.nodes.macro_analyst import macro_analyst_node
from equity_agent.nodes.new_investment import new_investment_node
from equity_agent.nodes.portfolio_check import portfolio_check_node
from equity_agent.nodes.sector_analyst import sector_analyst_node
from equity_agent.nodes.signal_aggregator import signal_aggregator_node
from equity_agent.nodes.trade_analyst import trade_analyst_node
from equity_agent.state import AgentState


def route_portfolio_decision(state: AgentState) -> str:
    """Conditional edge function -- reads state, returns the next node's name."""
    return "existing_holding" if state["in_portfolio"] else "new_investment"


# ---------- Graph wiring ----------
graph = StateGraph(AgentState)

graph.add_node("fundamentals_analyst", fundamentals_analyst_node)
graph.add_node("macro_analyst", macro_analyst_node)
graph.add_node("sector_analyst", sector_analyst_node)
graph.add_node("competition_analyst", competition_analyst_node)
graph.add_node("signal_aggregator", signal_aggregator_node)
graph.add_node("portfolio_check", portfolio_check_node)
graph.add_node("existing_holding", existing_holding_node)
graph.add_node("new_investment", new_investment_node)
graph.add_node("trade_analyst", trade_analyst_node)
graph.add_node("build_trade_plan", build_trade_plan_node)
graph.add_node("log_and_alert", log_and_alert_node)

# Unconditional parallel fan-out: all four analysts always run.
for analyst in ("fundamentals_analyst", "macro_analyst", "sector_analyst", "competition_analyst"):
    graph.add_edge(START, analyst)
    graph.add_edge(analyst, "signal_aggregator")

graph.add_edge("signal_aggregator", "portfolio_check")

graph.add_conditional_edges(
    "portfolio_check",
    route_portfolio_decision,
    {
        "existing_holding": "existing_holding",
        "new_investment": "new_investment",
    },
)

graph.add_edge("existing_holding", "trade_analyst")
graph.add_edge("new_investment", "trade_analyst")
graph.add_edge("trade_analyst", "build_trade_plan")
graph.add_edge("build_trade_plan", "log_and_alert")
graph.add_edge("log_and_alert", END)

app = graph.compile()


# ---------- Run ----------
if __name__ == "__main__":
    result = app.invoke(
        {
            "ticker": "INFY.NS",
            "messages": [HumanMessage(content="Research Infosys Ltd.")],
        }
    )
    print(result["trade_plan"])
