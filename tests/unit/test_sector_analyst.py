# ABOUTME: Unit test for sector_analyst_node -- verifies it delegates to the shared
# ABOUTME: cache-aware fetch with the right (kind, doc_type) and maps the result into state.

from unittest.mock import MagicMock, patch

from equity_agent.nodes import sector_analyst
from equity_agent.nodes.sector_analyst import sector_analyst_node

SIGNAL = {"summary": "Sector demand softening.", "score": -0.2, "confidence": 0.6}


def test_returns_sector_signal_from_cache_aware_fetch():
    with patch(
        "equity_agent.nodes.sector_analyst.fetch_cache_aware_signal",
        MagicMock(return_value=SIGNAL),
    ) as mock_fetch:
        result = sector_analyst_node({"ticker": "TCS.NS"})

    mock_fetch.assert_called_once_with("TCS.NS", "sector", "sector_report", sector_analyst._PROMPT)
    assert result == {"sector_signal": SIGNAL}
