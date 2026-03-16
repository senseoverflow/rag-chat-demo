# RAG + LLM Demo

A minimal **Retrieval-Augmented Generation (RAG)** demo that mirrors the flow of a production app (e.g. BioCourt): **Python backend** (embed → vector search → LLM) + **Flutter chat UI** that sends questions and shows answers with **sources** (retrieved chunks).

## What it does

- **Backend (Python):** Ingest docs → chunk → embed (Gemini) → in-memory vector store → on query: retrieve top-k chunks → build prompt → LLM answer. Optional **HTTP API** (`/query`, `/health`) for the app.
- **App (Flutter):** Chat-style screen: user message → POST to API → display answer and expandable “sources” (the chunks used for context), same idea as a coach chat with RAG context.

## Requirements

- Python 3.10+ and a [Gemini API key](https://ai.google.dev/gemini-api/docs) (free tier is enough)
- Flutter SDK (for the app)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key
```

## Usage

### 1. Index documents (once or when docs change)

```bash
python main.py index
```

Reads `sample_docs/*.txt`, chunks, embeds with Gemini, saves to `index.json`.

### 2. CLI query (optional)

```bash
python main.py query "What is the refund policy?"
```

### 3. Run the API (for the Flutter app)

```bash
source .venv/bin/activate
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run the Flutter app

```bash
cd app
flutter pub get
flutter run
```

- **iOS Simulator:** uses `http://localhost:8000` (default in `app/lib/main.dart`).
- **Android Emulator:** change the base URL in `app/lib/main.dart` to `http://10.0.2.2:8000` so the emulator can reach the host.

Then type a question in the chat (e.g. “What is the refund policy?”); the answer and the “sources” used for context are shown.

## Project layout

```
demo-rag-llm/
├── README.md
├── requirements.txt
├── .env.example
├── main.py             # CLI: index | query
├── api.py              # FastAPI: POST /query (question → answer + sources), GET /health
├── embed_store.py      # Embedding + in-memory vector store + retrieval
├── llm.py              # LLM call (Gemini)
├── rag.py              # RAG pipeline: retrieve → build prompt → LLM; answer_with_sources for API
├── sample_docs/        # Example .txt documents to index
└── app/                # Flutter app (chat UI, calls API)
    ├── lib/
    │   ├── main.dart
    │   ├── models/chat_message.dart
    │   ├── screens/chat_screen.dart   # Chat + expandable sources (BioCourt-style)
    │   └── services/rag_api_client.dart
    └── pubspec.yaml
```

## Customization

- **Your own docs:** Put more `.txt` files in `sample_docs/` and run `python main.py index` again.
- **Chunk size / overlap:** Edit `CHUNK_SIZE` and `CHUNK_OVERLAP` in `embed_store.py`.
- **Top-K:** Change `TOP_K` in `rag.py` to retrieve more or fewer chunks.
- **Other backends:** Swap `embed_store.py` for a vector DB (e.g. Chroma, pgvector) and keep the same `rag.py` interface.
- **App base URL:** Edit `_kRagBaseUrl` in `app/lib/main.dart` for a different API host/port.

## Note

This demo uses the `google-generativeai` Python package. You may see a deprecation warning; the package still works. For new projects you can consider the `google-genai` SDK instead.

## License

MIT.
