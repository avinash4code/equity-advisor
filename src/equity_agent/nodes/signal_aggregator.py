# ABOUTME: Signal aggregator node -- synthesizes fundamentals, macro, sector, and competition
# ABOUTME: signals into one weighed summary and confidence score.

from pydantic import BaseModel

from equity_agent.llm import llm
from equity_agent.state import AgentState


class _AggregatedSignal(BaseModel):
    summary: str
    confidence: float


def signal_aggregator_node(state: AgentState) -> dict:
    prompt = (
        "Weigh the following signals for the same company and produce a single synthesized "
        "judgment. Respond with a JSON object with exactly these keys: summary, confidence (0..1).\n\n"
        f"Fundamentals: {state.get('fundamentals')}\n"
        f"Macro: {state.get('macro_signal')}\n"
        f"Sector: {state.get('sector_signal')}\n"
        f"Competition: {state.get('competition_signal')}"
    )
    # method="json_mode": matches fundamentals_analyst's workaround for the deepseek-backed LLM.
    synthesizer = llm.with_structured_output(_AggregatedSignal, method="json_mode")
    result = synthesizer.invoke(prompt)
    aggregated = result.model_dump()
    return {"aggregated_signal": aggregated, "confidence": aggregated["confidence"]}
