# ABOUTME: Shared LLM client, configured from LLM_PROVIDER/LLM_MODEL/LLM_API_KEY in .env.
# ABOUTME: Node modules import `llm` from here rather than from graph.py, to avoid circular imports.

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # swap for your LLM of choice

load_dotenv()

LLM_PROVIDER = os.environ["LLM_PROVIDER"]
LLM_MODEL = os.environ["LLM_MODEL"]
LLM_API_KEY = os.environ["LLM_API_KEY"]

if LLM_PROVIDER == "deepseek":
    llm = ChatOpenAI(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        base_url="https://api.deepseek.com",
        temperature=0,
    )
elif LLM_PROVIDER == "openai":
    llm = ChatOpenAI(model=LLM_MODEL, api_key=LLM_API_KEY, temperature=0)
else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
