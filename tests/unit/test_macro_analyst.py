# ABOUTME: Unit test for macro_analyst_node -- verifies it delegates to the shared
# ABOUTME: cache-aware fetch with the right (kind, doc_type) and maps the result into state.

from unittest.mock import MagicMock, patch

from equity_agent.nodes import macro_analyst
from equity_agent.nodes.macro_analyst import macro_analyst_node

SIGNAL = {"summary": "Rate cuts likely.", "score": 0.4, "confidence": 0.7}


def test_returns_macro_signal_from_cache_aware_fetch():
    with patch(
        "equity_agent.nodes.macro_analyst.fetch_cache_aware_signal",
        MagicMock(return_value=SIGNAL),
    ) as mock_fetch:
        result = macro_analyst_node({"ticker": "TCS.NS"})

    mock_fetch.assert_called_once_with("TCS.NS", "macro", "macro_note", macro_analyst._PROMPT)
    assert result == {"macro_signal": SIGNAL}
