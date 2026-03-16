"""
RAG pipeline: retrieve relevant chunks for a query, build a prompt with context, call LLM.
"""

from embed_store import load_index, retrieve
from llm import generate

TOP_K = 4


def build_prompt(query: str, context_chunks: list[str]) -> str:
    """Build a single prompt with retrieved context and the user question."""
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(No relevant context found.)"
    return f"""You are a helpful assistant. Answer the question below using only the provided context. If the context does not contain enough information, say so briefly. Keep the answer concise.

Context:
{context}

Question: {query}

Answer:"""


def answer(api_key: str, query: str, index_path: str = "index.json", top_k: int = TOP_K) -> str:
    """
    Run RAG: load index, retrieve top_k chunks for query, build prompt, return LLM answer.
    """
    index = load_index(index_path)
    chunks = retrieve(api_key, query, index, top_k=top_k)
    prompt = build_prompt(query, chunks)
    return generate(api_key, prompt)


def answer_with_sources(
    api_key: str, query: str, index_path: str = "index.json", top_k: int = TOP_K
) -> tuple[str, list[str]]:
    """
    Run RAG and return (answer, list of source chunk texts used as context).
    """
    index = load_index(index_path)
    chunks = retrieve(api_key, query, index, top_k=top_k)
    prompt = build_prompt(query, chunks)
    answer_text = generate(api_key, prompt)
    return answer_text, chunks
