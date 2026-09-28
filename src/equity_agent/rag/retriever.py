# ABOUTME: Metadata-filtered lookups against the shared Chroma collection, distinct from
# ABOUTME: rag_retrieve_node's semantic similarity_search -- this finds the latest doc by date, not by meaning.

from langchain_community.vectorstores import Chroma

from equity_agent.rag.ingest import _get_vectorstore


def get_latest_document(ticker: str, doc_type: str, vectorstore: Chroma | None = None) -> dict | None:
    """Returns the most recent indexed doc for `ticker`/`doc_type`, or None if none is indexed.

    Result shape: {"text": str, "report_period": str, "report_date": str}.
    """
    store = vectorstore if vectorstore is not None else _get_vectorstore()
    matches = store.get(
        where={
            "$and": [
                {"ticker": {"$eq": ticker}},
                {"doc_type": {"$eq": doc_type}},
            ]
        },
        include=["documents", "metadatas"],
    )
    if not matches["ids"]:
        return None

    documents = matches["documents"]
    metadatas = matches["metadatas"]
    latest_idx = max(range(len(metadatas)), key=lambda i: metadatas[i]["report_date"])
    return {
        "text": documents[latest_idx],
        "report_period": metadatas[latest_idx]["report_period"],
        "report_date": metadatas[latest_idx]["report_date"],
    }


def get_latest_quarterly_report(ticker: str, vectorstore: Chroma | None = None) -> dict | None:
    return get_latest_document(ticker, "quarterly_report", vectorstore=vectorstore)
