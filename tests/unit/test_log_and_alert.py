# ABOUTME: Unit tests for log_and_alert_node -- mocks the DB write and send_alert,
# ABOUTME: verifies the alert only fires when verdict == "flag".

from unittest.mock import MagicMock, patch

from equity_agent.nodes.log_and_alert import log_and_alert_node

STATE = {
    "ticker": "TCS.NS",
    "confidence": 0.55,
    "aggregated_signal": {"summary": "Mixed signals, mild headwind from competition."},
}


def _patched():
    mocks = {"_log_verdict": MagicMock(), "send_alert": MagicMock()}
    return patch.multiple("equity_agent.nodes.log_and_alert", **mocks), mocks


def test_flag_verdict_logs_and_sends_alert():
    patcher, mocks = _patched()
    with patcher:
        log_and_alert_node({**STATE, "verdict": "flag"})

    mocks["_log_verdict"].assert_called_once_with(
        "TCS.NS", "flag", 0.55, "Mixed signals, mild headwind from competition."
    )
    mocks["send_alert"].assert_called_once_with("TCS.NS", "Mixed signals, mild headwind from competition.")


def test_no_action_verdict_logs_without_alert():
    patcher, mocks = _patched()
    with patcher:
        log_and_alert_node({**STATE, "verdict": "no_action"})

    mocks["_log_verdict"].assert_called_once()
    mocks["send_alert"].assert_not_called()


def test_need_more_data_verdict_logs_without_alert():
    patcher, mocks = _patched()
    with patcher:
        log_and_alert_node({**STATE, "verdict": "need_more_data"})

    mocks["send_alert"].assert_not_called()
