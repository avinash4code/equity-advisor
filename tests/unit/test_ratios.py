# ABOUTME: Unit tests for the pure _compute_ratios function -- no I/O, just edge cases.

from equity_agent.nodes.fundamentals_analyst import _compute_ratios


def test_computes_all_ratios_when_all_inputs_present():
    raw = {
        "price": 2200.0,
        "shares_outstanding": 3600000000,
        "eps": 36.9,
        "net_income": 133490000000.0,
        "revenue": 722750000000.0,
        "revenue_prior_year": 634370000000.0,
        "total_equity": 1072400000000.0,
        "total_debt": 112830000000.0,
    }
    ratios = _compute_ratios(raw)
    assert ratios["pe_ratio"] == 2200.0 / 36.9
    assert ratios["eps"] == 36.9
    assert ratios["market_cap"] == 2200.0 * 3600000000
    assert ratios["roe"] == 133490000000.0 / 1072400000000.0
    assert ratios["debt_to_equity"] == 112830000000.0 / 1072400000000.0
    assert ratios["revenue_growth_yoy"] == (722750000000.0 / 634370000000.0) - 1


def test_missing_inputs_produce_none_not_crash():
    raw = {
        "price": None,
        "shares_outstanding": None,
        "eps": None,
        "net_income": 100.0,
        "revenue": 500.0,
        "revenue_prior_year": None,
        "total_equity": None,
        "total_debt": None,
    }
    ratios = _compute_ratios(raw)
    assert ratios == {
        "pe_ratio": None,
        "eps": None,
        "market_cap": None,
        "roe": None,
        "debt_to_equity": None,
        "revenue_growth_yoy": None,
    }


def test_zero_equity_does_not_raise_division_error():
    raw = {
        "price": 100.0,
        "shares_outstanding": 10.0,
        "eps": 5.0,
        "net_income": 50.0,
        "revenue": 200.0,
        "revenue_prior_year": 180.0,
        "total_equity": 0.0,
        "total_debt": 20.0,
    }
    ratios = _compute_ratios(raw)
    assert ratios["roe"] is None
    assert ratios["debt_to_equity"] is None
    assert ratios["pe_ratio"] == 20.0
