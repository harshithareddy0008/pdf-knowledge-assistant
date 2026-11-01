"""FastAPI application; per-browser UUID workspace and shared server-side token."""
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from backend.config import get_settings
from backend.schemas import AskRequest, AskResponse, DocumentsResponse, UploadResponse
from backend.security import get_workspace, require_token
from backend.services.pdf_service import PDFValidationError
from backend.services.rag import answer_question, index_file
from backend.services.store import list_documents, make_store

app = FastAPI(title="PDF Knowledge Assistant API", version="1.0.0")
Protected = Annotated[None, Depends(require_token)]
Workspace = Annotated[str, Depends(get_workspace)]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(files: Annotated[list[UploadFile], File()], _auth: Protected, workspace: Workspace):
    settings = get_settings()
    if not 1 <= len(files) <= settings.max_files_per_request:
        raise HTTPException(status_code=422, detail=f"Upload 1–{settings.max_files_per_request} PDFs at once.")
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    store = make_store(workspace, settings)
    result = []
    for file in files:
        # Read only max+1 bytes to avoid unbounded uploads into memory.
        payload = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
        await file.close()
        try:
            result.append(index_file(store, payload, file.filename or "document.pdf", settings))
        except PDFValidationError as exc:
            raise HTTPException(status_code=422, detail=f"{file.filename}: {exc}") from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Document indexing failed. Check API logs and Gemini embedding quota.") from exc
    return {"results": result}


@app.get("/documents", response_model=DocumentsResponse)
def documents(_auth: Protected, workspace: Workspace):
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    return {"documents": list_documents(make_store(workspace, settings))}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, _auth: Protected, workspace: Workspace):
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    try:
        return answer_question(make_store(workspace, settings), request.question, settings)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Gemini/RAG request failed. Check backend logs or API quota.") from exc


@app.delete("/documents")
def reset_documents(_auth: Protected, workspace: Workspace):
    settings = get_settings()
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")
    store = make_store(workspace, settings)
    store.delete_collection()
    return {"status": "cleared"}
