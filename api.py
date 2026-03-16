"""
Minimal HTTP API for the RAG demo. Exposes POST /query (question -> answer + sources)
so a Flutter (or other) client can drive a chat-style UI.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import answer_with_sources

load_dotenv()


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set GEMINI_API_KEY in .env")
    return key


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload API key at startup
    try:
        get_api_key()
    except RuntimeError as e:
        print(f"Warning: {e}. /query will fail until .env is set.")
    yield


app = FastAPI(title="RAG Demo API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    q = (request.question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="question is required")
    try:
        api_key = get_api_key()
        answer_text, sources = answer_with_sources(api_key, q)
        return QueryResponse(answer=answer_text, sources=sources or [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
