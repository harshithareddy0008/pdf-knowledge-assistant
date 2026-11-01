"""Memory-only text extraction of PDFs, preserving original page references."""
import hashlib
import re
from pathlib import PurePosixPath

import fitz
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import Settings


class PDFValidationError(ValueError):
    pass


def safe_filename(filename: str) -> str:
    cleaned = PurePosixPath(filename.replace("\\", "/")).name
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", cleaned).strip()
    return cleaned[:120] or "document.pdf"


def extract_chunks(payload: bytes, filename: str, settings: Settings) -> tuple[str, int, list[Document]]:
    name = safe_filename(filename)
    if not name.lower().endswith(".pdf") or not payload.startswith(b"%PDF-"):
        raise PDFValidationError("Upload a valid PDF file (.pdf).")
    if len(payload) > settings.max_upload_mb * 1024 * 1024:
        raise PDFValidationError(f"PDF must be {settings.max_upload_mb} MB or smaller.")
    file_id = hashlib.sha256(payload).hexdigest()[:24]
    try:
        with fitz.open(stream=payload, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise PDFValidationError("Password-protected PDFs are not supported.")
            if len(pdf) > settings.max_pdf_pages:
                raise PDFValidationError(f"Maximum {settings.max_pdf_pages} pages per PDF.")
            documents = []
            for index, page in enumerate(pdf):
                text = page.get_text("text").strip()
                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={"file": name, "file_id": file_id, "page": index + 1},
                        )
                    )
    except PDFValidationError:
        raise
    except (RuntimeError, ValueError, TypeError) as exc:
        raise PDFValidationError("Could not read PDF. Please use a valid, unencrypted file.") from exc
    if not documents:
        raise PDFValidationError("No selectable text found. Scanned PDFs need OCR, which this version does not include.")
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=140)
    chunks = splitter.split_documents(documents)
    if len(chunks) > 600:
        raise PDFValidationError("Too much extracted text. Try a smaller PDF.")
    return file_id, len(documents), chunks
