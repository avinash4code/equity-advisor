# ABOUTME: Unit tests for trade_analyst_node -- mocks the LLM, verifies the prompt carries
# ABOUTME: aggregated signal + position context and the decision maps into state.

from unittest.mock import MagicMock, patch

from equity_agent.nodes.trade_analyst import trade_analyst_node

DECISION = {"action": "add", "verdict": "flag", "rationale": "Sector headwind offset by strong fundamentals."}


def _mock_llm(decision):
    structured_result = MagicMock()
    structured_result.model_dump.return_value = decision
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value.invoke.return_value = structured_result
    return mock_llm


def test_prompt_includes_existing_holding():
    mock_llm = _mock_llm(DECISION)
    state = {
        "aggregated_signal": {"summary": "Mixed."},
        "confidence": 0.55,
        "holding": {"quantity": 10, "avg_price": 3850.0},
    }
    with patch("equity_agent.nodes.trade_analyst.llm", mock_llm):
        result = trade_analyst_node(state)

    prompt = mock_llm.with_structured_output.return_value.invoke.call_args.args[0]
    assert "Existing holding" in prompt
    assert "3850.0" in prompt
    assert result == {"trade_decision": DECISION, "verdict": "flag"}


def test_prompt_includes_invest_amount_when_not_held():
    mock_llm = _mock_llm(DECISION)
    state = {
        "aggregated_signal": {"summary": "Mixed."},
        "confidence": 0.55,
        "holding": None,
        "invest_amount": 50000.0,
    }
    with patch("equity_agent.nodes.trade_analyst.llm", mock_llm):
        trade_analyst_node(state)

    prompt = mock_llm.with_structured_output.return_value.invoke.call_args.args[0]
    assert "Not currently held" in prompt
    assert "50000.0" in prompt
