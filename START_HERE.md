# 🚀 START HERE — Project 02: PDF Knowledge Assistant

Instructions for a Windows PC with VS Code + PowerShell.

## 1. Open project folder

Unzip the downloaded archive. In VS Code: **File → Open Folder → `pdf-knowledge-assistant`**.

The terminal path must end in `pdf-knowledge-assistant`; `pyproject.toml` should be in the folder. Select **Terminal → New Terminal**.

## 2. Check tools

```powershell
python --version
git --version
uv --version
```

Use Python 3.11 or 3.12. If `uv` is not installed:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart the VS Code terminal if `uv` is still not found.

## 3. Configure Gemini key and shared secret

Sign in at https://aistudio.google.com/api-keys , create a Gemini API key and keep it private.

```powershell
Copy-Item .env.example .env
notepad .env
```

In `.env` set:

```dotenv
GEMINI_API_KEY=YOUR_REAL_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
APP_ACCESS_TOKEN=YOUR_LONG_RANDOM_PRIVATE_SECRET
API_BASE_URL=http://127.0.0.1:8000
DATA_DIR=./data
```

For a long random secret run:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated value into `APP_ACCESS_TOKEN`. NEVER post `.env` or share the Gemini key/token. `.env.example` must contain dummy values only.

## 4. Install dependencies

```powershell
uv sync
```

Internet is required for this step. Initial Chroma installation might take a little time.

## 5. Check both Gemini models

```powershell
uv run python -m scripts.check_gemini
```

You should see a generated `READY` response and embedding dimensions `768` (wording of generated text may vary). If you see `404 model not found`, choose an available generation model in Google AI Studio. If you see `429`, check Gemini API quotas.

## 6. Start FastAPI (Terminal 1)

```powershell
uv run uvicorn backend.main:app --reload
```

Open:

- http://127.0.0.1:8000/health (should show `{"status":"ok"}`)
- http://127.0.0.1:8000/docs (interactive API documentation)

## 7. Start Streamlit (Terminal 2)

Open another **Terminal → New Terminal** in the same project folder:

```powershell
uv run python -m streamlit run frontend/app.py
```

Open http://localhost:8501

The `python -m streamlit` form keeps the project root on Python's import path, avoiding the `No module named frontend` issue you saw in Project 01.

## 8. Your first RAG test

1. Make a small text-based PDF in MS Word/Google Docs containing a few paragraphs. See `examples/sample_notes.txt` for example text.
2. Streamlit sidebar → **Choose PDF files** → select your PDF.
3. Click **Process PDFs**. Wait for `indexed` confirmation.
4. Click **Refresh indexed PDFs** to view the indexed file.
5. Chat: `According to my document, how is regression different from classification?`
6. Check generated answer and **Retrieved PDF sources** showing page references.
7. Ask something not in the PDF, e.g. `What is today's stock market price?` The assistant is instructed to say the PDF doesn't contain the answer (LLMs can still make mistakes).

## 9. Run offline tests

```powershell
uv run pytest -q
```

These tests mock Gemini and Chroma, so you don't pay for API calls. Step 5 and Step 8 ARE live integration checks.

## 10. Push to GitHub

Create an empty public repo named `pdf-knowledge-assistant` at https://github.com/new (do not create another README on GitHub).

```powershell
git init
git branch -M main
git add .
git status
```

**STOP and check** `git status`: `.env`, `.venv`, and `data` must not be staged! Then:

```powershell
git commit -m "Initial commit: Gemini RAG PDF Knowledge Assistant"
git remote add origin https://github.com/harshithareddy0008/pdf-knowledge-assistant.git
git push -u origin main
```

If `origin` exists, use `git remote set-url origin ...` instead of adding it again.

## 11. Deploy to Render

### API first

Create a **Web Service** from GitHub repository:

- Name: `pdf-knowledge-assistant-api`
- Runtime: Python
- Build command: `pip install uv && uv sync --no-dev`
- Start command: `uv run --no-sync uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Environment: `GEMINI_API_KEY` (real key), `GEMINI_MODEL` (working model), `GEMINI_EMBEDDING_MODEL=gemini-embedding-001`, `APP_ACCESS_TOKEN` (the same private token), `PYTHON_VERSION=3.11.11`
- Root directory: blank
- Health check `/health`

When live, test `https://YOUR-API-URL.onrender.com/health`. The returned `ok` only confirms the server is up, not the Gemini connection.

### Streamlit UI second

Create another **Web Service** from the same repository:

- Name: `pdf-knowledge-assistant-ui`
- Runtime: Python
- Build command: `pip install uv && uv sync --no-dev`
- Start command: `uv run --no-sync python -m streamlit run frontend/app.py --server.address 0.0.0.0 --server.port $PORT`
- Environment: `API_BASE_URL=https://YOUR-API-URL.onrender.com` (no trailing `/health`), `APP_ACCESS_TOKEN` (exact same secret), `PYTHON_VERSION=3.11.11`
- Root directory: blank

Then test uploading and answering using the public Streamlit URL.

**Render Free caveat:** Free services can sleep, and their local filesystem is **ephemeral**. Chroma data can disappear on restart/redeploy. This is a learning demo, not persistent production storage. Use a paid persistent disk or managed vector database before claiming production durability. Free plan availability/resources may change.

## Troubleshooting

- `ModuleNotFoundError: frontend`: run `uv run python -m streamlit run frontend/app.py`, from the root.
- `401`: mismatched `APP_ACCESS_TOKEN` between UI and API.
- `503`: missing `GEMINI_API_KEY` or `APP_ACCESS_TOKEN`.
- `404 Gemini model`: configure a currently supported model ID.
- `429`: API quota/rate limits; retry later or adjust usage.
- `502` on upload: inspect API logs. Embedding calls require a working Gemini key and model/quota.
- Blank/scanned PDF: OCR not included. Use text-based PDFs.
- API connection error: start FastAPI or correct `API_BASE_URL`.
- `Chroma` installation/build problem: prefer Python 3.11 (64-bit).

## Security and scope

This is a portfolio demo, **not a multi-user production service**: shared UI-to-API token (no login), unguessable browser workspace IDs, API quotas not enforced, no OCR, no guaranteed answer accuracy. Text from uploaded PDFs is sent to Google Gemini to create embeddings and answer questions. Avoid confidential PDFs. Public users may trigger usage costs on the API key.
