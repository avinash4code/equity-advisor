"""
ABOUTME: Rebuilds equity_research.db from schema.sql and inserts sample rows for TCS.NS.
ABOUTME: Dev-only seed script; safe to rerun, always starts from a clean database.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "equity_research.db"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "src" / "db" / "schema.sql"


def main() -> None:
    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_PATH.read_text())

    conn.execute(
        "INSERT INTO fundamentals "
        "(ticker, as_of_date, pe_ratio, eps, market_cap, roe, debt_to_equity, revenue_growth_yoy) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("TCS.NS", "2026-09-01", 28.4, 134.2, 13650000000000, 0.52, 0.08, 0.061),
    )
    conn.execute(
        "INSERT INTO watchlist (ticker, added_at, notes) VALUES (?, ?, ?)",
        ("TCS.NS", "2026-01-15", "Core IT holding, watch margin trends"),
    )
    conn.execute(
        "INSERT INTO portfolio (ticker, quantity, avg_price, bought_at) VALUES (?, ?, ?, ?)",
        ("TCS.NS", 10, 3850.0, "2025-03-10"),
    )
    conn.execute(
        "INSERT INTO verdicts (ticker, verdict, confidence, summary, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        ("TCS.NS", "no_action", 0.72, "Fundamentals in line with sector, no anomaly.", "2026-09-01"),
    )

    conn.commit()
    conn.close()
    print(f"Seeded {DB_PATH}")


if __name__ == "__main__":
    main()
