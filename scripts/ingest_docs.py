# ABOUTME: CLI to embed a single report file into the shared Chroma collection.
# ABOUTME: Usage: python scripts/ingest_docs.py <ticker> <doc_type> <report_period> <report_date> <file>

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from equity_agent.rag.ingest import ingest_document


def main() -> None:
    if len(sys.argv) != 6:
        print(
            "Usage: python scripts/ingest_docs.py <ticker> <doc_type> "
            "<report_period> <report_date> <file>"
        )
        sys.exit(1)

    ticker, doc_type, report_period, report_date, file_path = sys.argv[1:]
    text = Path(file_path).read_text()
    ingest_document(ticker, doc_type, report_period, report_date, text)
    print(f"Ingested {file_path} for {ticker} ({doc_type}, {report_period})")


if __name__ == "__main__":
    main()
