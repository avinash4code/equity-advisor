# ABOUTME: Metadata-filtered lookups against the shared Chroma collection, distinct from
# ABOUTME: rag_retrieve_node's semantic similarity_search -- this finds the latest doc by date, not by meaning.

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from equity_agent.rag.ingest import COLLECTION_NAME, PERSIST_DIRECTORY


def _get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddings(),
        persist_directory=PERSIST_DIRECTORY,
    )


def get_latest_quarterly_report(ticker: str, vectorstore: Chroma | None = None) -> dict | None:
    """Returns the most recent quarterly report doc for `ticker`, or None if none is indexed.

    Result shape: {"text": str, "report_period": str, "report_date": str}.
    """
    store = vectorstore if vectorstore is not None else _get_vectorstore()
    matches = store.get(
        where={
            "$and": [
                {"ticker": {"$eq": ticker}},
                {"doc_type": {"$eq": "quarterly_report"}},
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
