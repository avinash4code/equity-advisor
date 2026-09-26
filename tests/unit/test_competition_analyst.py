# ABOUTME: Unit test for competition_analyst_node -- verifies it delegates to the shared
# ABOUTME: cache-aware fetch with the right (kind, doc_type) and maps the result into state.

from unittest.mock import MagicMock, patch

from equity_agent.nodes import competition_analyst
from equity_agent.nodes.competition_analyst import competition_analyst_node

SIGNAL = {"summary": "Losing share to a lower-cost entrant.", "score": -0.5, "confidence": 0.65}


def test_returns_competition_signal_from_cache_aware_fetch():
    with patch(
        "equity_agent.nodes.competition_analyst.fetch_cache_aware_signal",
        MagicMock(return_value=SIGNAL),
    ) as mock_fetch:
        result = competition_analyst_node({"ticker": "TCS.NS"})

    mock_fetch.assert_called_once_with(
        "TCS.NS", "competition", "competitor_analysis", competition_analyst._PROMPT
    )
    assert result == {"competition_signal": SIGNAL}
