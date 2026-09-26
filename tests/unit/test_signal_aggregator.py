# ABOUTME: Unit test for signal_aggregator_node -- mocks the LLM, verifies all four inputs
# ABOUTME: reach the prompt and the structured result maps into state correctly.

from unittest.mock import MagicMock, patch

from equity_agent.nodes.signal_aggregator import signal_aggregator_node

STATE = {
    "ticker": "TCS.NS",
    "fundamentals": {"pe_ratio": 28.4},
    "macro_signal": {"summary": "Rate cuts likely.", "score": 0.4, "confidence": 0.7},
    "sector_signal": {"summary": "Sector demand softening.", "score": -0.2, "confidence": 0.6},
    "competition_signal": {"summary": "Losing share.", "score": -0.5, "confidence": 0.65},
}


def test_aggregates_all_four_signals_into_state():
    structured_result = MagicMock()
    structured_result.model_dump.return_value = {
        "summary": "Mixed signals, mild headwind from competition.",
        "confidence": 0.55,
    }
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = structured_result

    with patch("equity_agent.nodes.signal_aggregator.llm", mock_llm):
        result = signal_aggregator_node(STATE)

    prompt = mock_llm.with_structured_output.return_value.invoke.call_args.args[0]
    assert "pe_ratio" in prompt
    assert "Rate cuts likely" in prompt
    assert "Sector demand softening" in prompt
    assert "Losing share" in prompt

    assert result == {
        "aggregated_signal": {"summary": "Mixed signals, mild headwind from competition.", "confidence": 0.55},
        "confidence": 0.55,
    }
