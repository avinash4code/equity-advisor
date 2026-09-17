# ABOUTME: Embeds source documents (quarterly reports, earnings calls, analyst notes) into the
# ABOUTME: shared Chroma collection, tagged with metadata the retriever filters/sorts on.

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

COLLECTION_NAME = "equity_docs"
PERSIST_DIRECTORY = "./chroma_db"


def _get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddings(),
        persist_directory=PERSIST_DIRECTORY,
    )


def ingest_document(
    ticker: str,
    doc_type: str,
    report_period: str,
    report_date: str,
    text: str,
    vectorstore: Chroma | None = None,
) -> None:
    """Embeds `text` with metadata {ticker, doc_type, report_period, report_date}.

    report_date must be an ISO date string (e.g. "2026-07-15") -- the retriever
    sorts on it to find the latest report for a ticker.
    """
    store = vectorstore if vectorstore is not None else _get_vectorstore()
    store.add_texts(
        texts=[text],
        metadatas=[
            {
                "ticker": ticker,
                "doc_type": doc_type,
                "report_period": report_period,
                "report_date": report_date,
            }
        ],
    )
