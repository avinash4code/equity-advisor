-- ABOUTME: RDBMS schema for fundamentals, watchlist, portfolio, and verdicts.
-- ABOUTME: SQLite-compatible; ticker string (e.g. "TCS.NS") is the natural key throughout.

CREATE TABLE fundamentals (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker              TEXT NOT NULL,
    as_of_date          TEXT NOT NULL,          -- ISO date; one snapshot per pull
    pe_ratio            REAL,
    eps                 REAL,
    market_cap          REAL,
    roe                 REAL,
    debt_to_equity      REAL,
    revenue_growth_yoy  REAL,
    UNIQUE (ticker, as_of_date)
);
CREATE INDEX idx_fundamentals_ticker ON fundamentals (ticker, as_of_date DESC);

CREATE TABLE watchlist (
    ticker      TEXT PRIMARY KEY,
    added_at    TEXT NOT NULL,
    notes       TEXT
);

-- one row per buy lot, not an aggregated position, so holding period and
-- STCG/LTCG treatment can be computed per lot rather than off a blended average
CREATE TABLE portfolio (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker      TEXT NOT NULL,
    quantity    REAL NOT NULL,
    avg_price   REAL NOT NULL,
    bought_at   TEXT NOT NULL
);
CREATE INDEX idx_portfolio_ticker ON portfolio (ticker);

-- one row per reasoning-node run
CREATE TABLE verdicts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker      TEXT NOT NULL,
    verdict     TEXT NOT NULL CHECK (verdict IN ('flag', 'no_action', 'need_more_data')),
    confidence  REAL NOT NULL,
    summary     TEXT NOT NULL,          -- reasoning node's synthesized text
    created_at  TEXT NOT NULL
);
CREATE INDEX idx_verdicts_ticker ON verdicts (ticker, created_at DESC);
