# ABOUTME: Embeds source documents (quarterly reports, earnings calls, analyst notes) into the
# ABOUTME: shared Chroma collection, tagged with metadata the retriever filters/sorts on.

import threading

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

COLLECTION_NAME = "equity_docs"
PERSIST_DIRECTORY = "./chroma_db"
EMBEDDING_MODEL = "nomic-ai/nomic-embed-text-v1.5"

_vectorstore_lock = threading.Lock()
_vectorstore: Chroma | None = None


def _get_vectorstore() -> Chroma:
    # Locked (not just cached) so concurrent callers -- the graph runs multiple
    # analyst nodes in parallel threads -- share one Chroma client instead of
    # racing to initialize the same on-disk store, which corrupts it. A plain
    # lru_cache doesn't help here: its lock only guards the cache dict, not the
    # wrapped call, so concurrent misses still construct Chroma() twice.
    global _vectorstore
    with _vectorstore_lock:
        if _vectorstore is None:
            _vectorstore = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL, model_kwargs={"trust_remote_code": True}
                ),
                persist_directory=PERSIST_DIRECTORY,
            )
        return _vectorstore


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
