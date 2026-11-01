# 📚 PDF Knowledge Assistant — Project 02 (Gemini + RAG)

A portfolio-ready, full-stack **Retrieval-Augmented Generation (RAG)** demonstration built using Google Gemini, LangChain, ChromaDB, FastAPI, Streamlit and PyMuPDF.

> Complete beginner setup and Render steps: **[START_HERE.md](START_HERE.md)**

## Features

- Upload up to four text-based PDF files per upload (each up to 8 MB and 80 pages).
- Extract text and maintain page numbers using PyMuPDF.
- Split content into overlapping chunks using LangChain.
- Generate Gemini embeddings with task types `RETRIEVAL_DOCUMENT` and `RETRIEVAL_QUERY`.
- Store vectors in ChromaDB; isolate per-browser workspaces in UUID-based collections.
- Ask PDF-related questions using retrieval plus Gemini (answers request numbered references like `[1]`).
- Show retrieved source snippets and original PDF page numbers.
- Duplicate PDF detection, list indexed PDFs, clear workspace, and session-only UI chat history.
- FastAPI health endpoint, validation, environment-based secrets, offline unit tests, and Render configuration.

## Architecture

```text
Streamlit UI
   |   POST /upload (PDF)
   v
FastAPI -> PyMuPDF (PDF to page-wise text)
            -> LangChain RecursiveCharacterTextSplitter
            -> Gemini Embeddings (document task)
            -> ChromaDB (workspace collection + metadata)

Streamlit UI
   |   POST /ask (question)
   v
FastAPI -> Gemini Embeddings (query task)
            -> ChromaDB similarity search (top-k passages)
            -> Gemini LLM (passages + question; grounded prompt)
            -> Answer + numbered retrieved PDF references
   |
   v
Streamlit chat display
```

## Backend API

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Availability check; no auth required |
| POST | `/upload` | Index multipart PDF uploads |
| GET | `/documents` | List indexed PDFs in workspace |
| POST | `/ask` | Ask question grounded in uploaded PDFs |
| DELETE | `/documents` | Clear current workspace collection |

Protected routes use `X-App-Token` (shared server-side token) and `X-Workspace-ID` (UUID4). **UUID workspaces are not a replacement for user authentication.**

## Files

```text
pdf-knowledge-assistant/
├── backend/
│   ├── main.py                # FastAPI endpoints
│   ├── config.py              # .env / settings
│   ├── security.py            # Shared secret + workspace UUID
│   ├── schemas.py             # Pydantic request/response models
│   └── services/
│       ├── pdf_service.py     # PyMuPDF page extraction and chunking
│       ├── embeddings.py      # Gemini embeddings adapter for LangChain
│       ├── store.py           # ChromaDB vector store per workspace
│       └── rag.py             # Index, retrieve and generate
├── frontend/
│   ├── app.py                 # Streamlit UI
│   └── api_client.py          # API HTTP client
├── scripts/check_gemini.py   # Live LLM + embedding connectivity check
├── tests/                   # Offline automated tests
├── .streamlit/config.toml
├── .env.example
├── .gitignore
├── pyproject.toml
├── render.yaml
├── START_HERE.md
└── README.md
```

## Quick start

```powershell
Copy-Item .env.example .env
# Edit .env with real GEMINI_API_KEY, APP_ACCESS_TOKEN
uv sync
uv run python -m scripts.check_gemini
# terminal 1:
uv run uvicorn backend.main:app --reload
# terminal 2:
uv run python -m streamlit run frontend/app.py
# tests:
uv run pytest -q
```

- Frontend: http://localhost:8501
- Backend docs: http://127.0.0.1:8000/docs
- Backend health: http://127.0.0.1:8000/health

## What makes it RAG?

Normal LLM: **Question → Gemini → Answer**.

RAG: **Question → embedding → retrieve relevant PDF passages from ChromaDB → Gemini with PDF context → cited answer**.

Retrieval can reduce unsupported answers but doesn't guarantee factual correctness. Sources are **retrieved candidate passages**, not independently verified proof.

## Limitations / future improvements

- Text PDFs only (scanned/image-based PDFs need OCR).
- No user accounts, RBAC, rate limiting, billing protection, or audit trail.
- Public demo users can consume Gemini quota; use with caution.
- Render free plan has ephemeral filesystem; Chroma persistence works on local disks, not reliably across free redeploys.
- Large PDFs, tables and complex layouts may parse imperfectly.
- Workspace secret is stored in Streamlit browser session, not persistent across new sessions.
- Improvements: OCR, hybrid retrieval, reranking, structured source verification, true authentication, persistent managed Chroma, observability, abuse/rate controls.

## Learning outcomes

RAG, chunking, embeddings, vector databases, semantic search, prompt grounding, API design, FastAPI, Streamlit, external AI API integration, application testing, Git and Render.

## Documentation

- [Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- [LangChain Chroma integration](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
- [Render FastAPI deployment](https://render.com/docs/deploy-fastapi)
