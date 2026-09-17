"""
LangGraph sketch: Indian equity research co-pilot
Stages: v0 (router -> reasoning) -> v1 (+ RAG) -> v2 (+ SQL)

This is a starting skeleton, not production code. Swap the placeholder
LLM/vectorstore/db calls for your real ones as you build.
"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
import sqlite3

from equity_agent.state import AgentState
from equity_agent.llm import llm


# ---------- v0: Router node ----------
def router_node(state: AgentState) -> dict:
    """Decides which data source(s) are needed for this query.

    v0/v1/v2 keep this simple: pick ONE branch. From v4 onward (once
    the live-data/MCP node exists too) you'll want this to return a
    list and fan out to multiple branches instead of picking just one.
    """
    prompt = f"""You are triaging a stock research request for {state['ticker']}.
Decide which single tool to call first. Respond with exactly one word:
"rag" or "sql".
"""
    response = llm.invoke(prompt)
    decision = "sql" if "sql" in response.content.lower() else "rag"
    return {
        "next_step": decision,
        "messages": state["messages"] + [AIMessage(content=f"Routing to: {decision}")],
    }


def route_decision(state: AgentState) -> str:
    """Conditional edge function -- reads state, returns the next node's name."""
    return state["next_step"]


# ---------- v1: RAG retrieve node ----------
def rag_retrieve_node(state: AgentState) -> dict:
    """Pulls relevant chunks from embedded earnings calls / annual reports / analyst notes."""
    from langchain_community.vectorstores import Chroma
    from langchain_openai import OpenAIEmbeddings

    vectorstore = Chroma(
        collection_name="equity_docs",
        embedding_function=OpenAIEmbeddings(),
        persist_directory="./chroma_db",
    )
    docs = vectorstore.similarity_search(state["ticker"], k=4)
    return {"retrieved_docs": [d.page_content for d in docs]}


# ---------- v2: SQL query node ----------
def sql_query_node(state: AgentState) -> dict:
    """Looks up fundamentals / watchlist history from the RDBMS."""
    conn = sqlite3.connect("equity_research.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT pe_ratio, eps, market_cap FROM fundamentals "
        "WHERE ticker = ? ORDER BY as_of_date DESC LIMIT 1",
        (state["ticker"],),
    )
    row = cur.fetchone()
    conn.close()

    result = {"pe_ratio": row[0], "eps": row[1], "market_cap": row[2]} if row else {}
    return {"sql_results": result}


# ---------- Reasoning node ----------
def reasoning_node(state: AgentState) -> dict:
    """v0: just echoes the routing decision. v1/v2: synthesizes whatever
    context has been gathered so far into a summary."""
    context = ""
    if state.get("retrieved_docs"):
        context += f"\nDocument excerpts: {state['retrieved_docs'][:2]}"
    if state.get("sql_results"):
        context += f"\nFundamentals: {state['sql_results']}"

    prompt = f"Summarize findings for {state['ticker']}.{context}"
    response = llm.invoke(prompt)
    return {"messages": state["messages"] + [AIMessage(content=response.content)]}


# ---------- Graph wiring ----------
graph = StateGraph(AgentState)

graph.add_node("router", router_node)
graph.add_node("rag_retrieve", rag_retrieve_node)
graph.add_node("sql_query", sql_query_node)
graph.add_node("reasoning", reasoning_node)

graph.set_entry_point("router")

# Conditional edge: router's decision determines which branch runs
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "rag": "rag_retrieve",
        "sql": "sql_query",
    },
)

graph.add_edge("rag_retrieve", "reasoning")
graph.add_edge("sql_query", "reasoning")
graph.add_edge("reasoning", END)

app = graph.compile()


# ---------- Run ----------
if __name__ == "__main__":
    result = app.invoke(
        {
            "ticker": "TCS.NS",
            "messages": [HumanMessage(content="Research TCS")],
            "retrieved_docs": [],
            "sql_results": {},
            "fundamentals": {},
            "next_step": None,
        }
    )
    print(result["messages"][-1].content)