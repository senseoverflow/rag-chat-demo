#!/usr/bin/env python3
"""
CLI for the RAG demo: index documents or run a query.
Usage:
  python main.py index
  python main.py query "Your question here"
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("Error: Set GEMINI_API_KEY in .env (copy from .env.example)", file=sys.stderr)
        sys.exit(1)
    return key


def cmd_index(api_key: str) -> None:
    from embed_store import embed_documents, save_index

    docs_dir = "sample_docs"
    print(f"Indexing .txt files from {docs_dir}...")
    chunks = embed_documents(api_key, docs_dir=docs_dir)
    save_index(chunks)
    print(f"Saved {len(chunks)} chunks to index.json")


def cmd_query(api_key: str, question: str) -> None:
    from rag import answer

    if not question.strip():
        print("Error: Provide a non-empty question", file=sys.stderr)
        sys.exit(1)
    print("Retrieving context and calling LLM...")
    response = answer(api_key, question)
    print(response)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py index | query \"Your question\"", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    cmd = sys.argv[1].lower()

    if cmd == "index":
        cmd_index(api_key)
    elif cmd == "query":
        if len(sys.argv) < 3:
            print('Usage: python main.py query "Your question"', file=sys.stderr)
            sys.exit(1)
        cmd_query(api_key, sys.argv[2])
    else:
        print(f"Unknown command: {cmd}. Use 'index' or 'query'.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
