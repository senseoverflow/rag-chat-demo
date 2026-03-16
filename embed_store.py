"""
Embedding and in-memory vector store with cosine-similarity retrieval.
Uses Gemini for embeddings; stores (text, vector) and supports top-k retrieval.
"""

import json
import os
import re
from pathlib import Path

import google.generativeai as genai
import numpy as np

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
INDEX_FILE = "index.json"


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks by character count."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        # Prefer breaking at sentence or line end
        for sep in ("\n\n", "\n", ". ", " "):
            if sep in chunk:
                last = chunk.rfind(sep)
                if last > chunk_size // 2:
                    chunk = chunk[: last + len(sep)].strip()
                    end = start + len(chunk)
        chunks.append(chunk.strip())
        start = end - overlap if end - overlap > start else end
        if start >= len(text):
            break
    return [c for c in chunks if c]


def _get_embedding(api_key: str, text: str) -> list[float]:
    """Get embedding for a single text using Gemini."""
    genai.configure(api_key=api_key)
    result = genai.embed_content(model="models/embedding-001", content=text)
    if isinstance(result, dict) and "embedding" in result:
        return result["embedding"]
    emb = getattr(result, "embedding", None)
    if emb is not None:
        return emb
    raise ValueError("Unexpected embedding result format")


def embed_documents(api_key: str, docs_dir: str = "sample_docs") -> list[dict]:
    """
    Load .txt files from docs_dir, chunk, embed with Gemini, return list of
    { "text": chunk, "embedding": [...] }.
    """
    docs_path = Path(docs_dir)
    if not docs_path.is_dir():
        raise FileNotFoundError(f"Docs directory not found: {docs_dir}")

    chunks_with_embeddings = []
    for path in sorted(docs_path.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        chunks = _chunk_text(text)
        for chunk in chunks:
            emb = _get_embedding(api_key, chunk)
            chunks_with_embeddings.append({"text": chunk, "embedding": emb})

    return chunks_with_embeddings


def save_index(chunks_with_embeddings: list[dict], path: str = INDEX_FILE) -> None:
    """Save chunks and embeddings to a JSON file (embeddings as lists)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks_with_embeddings, f, ensure_ascii=False, indent=0)


def load_index(path: str = INDEX_FILE) -> list[dict]:
    """Load index from JSON."""
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def retrieve(api_key: str, query: str, index: list[dict], top_k: int = 4) -> list[str]:
    """
    Embed query, compute cosine similarity against index, return top_k chunk texts.
    """
    if not index:
        return []
    q_emb = np.array(_get_embedding(api_key, query), dtype=np.float32)
    vectors = np.array([d["embedding"] for d in index], dtype=np.float32)
    # Cosine similarity
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1
    vectors_n = vectors / norms
    q_n = q_emb / (np.linalg.norm(q_emb) or 1)
    scores = np.dot(vectors_n, q_n)
    top_idxs = np.argsort(scores)[::-1][:top_k]
    return [index[i]["text"] for i in top_idxs]
