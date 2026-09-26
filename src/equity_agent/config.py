# ABOUTME: Shared constants for node behavior -- staleness thresholds and placeholder
# ABOUTME: values that stand in for data sources this project hasn't built yet.

# Cache-aware fetch nodes (fundamentals/macro/sector/competition analysts) treat a
# stored signal older than this as stale and re-derive it.
STALE_AFTER_DAYS = 100

# Placeholder for new_investment_node until a real cash/budget table exists.
DEFAULT_INVEST_AMOUNT = 50_000.0
