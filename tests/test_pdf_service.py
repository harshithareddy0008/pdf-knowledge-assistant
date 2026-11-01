"""Purely local PDF parsing tests: never call Gemini."""
import fitz
import pytest

from backend.config import Settings
from backend.services.pdf_service import PDFValidationError, extract_chunks, safe_filename


def make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    payload = doc.tobytes()
    doc.close()
    return payload


def test_extract_pdf_preserves_page_and_filename(tmp_path):
    payload = make_pdf("Supervised learning uses labeled training examples.")
    file_id, pages, chunks = extract_chunks(payload, "../../notes.pdf", Settings(data_dir=tmp_path))
    assert file_id
    assert pages == 1
    assert chunks[0].metadata["page"] == 1
    assert chunks[0].metadata["file"] == "notes.pdf"
    assert "Supervised learning" in chunks[0].page_content


def test_reject_non_pdf(tmp_path):
    with pytest.raises(PDFValidationError, match="valid PDF"):
        extract_chunks(b"Not a PDF", "notes.pdf", Settings(data_dir=tmp_path))


def test_scanned_or_blank_pdf_needs_ocr(tmp_path):
    with pytest.raises(PDFValidationError, match="OCR"):
        extract_chunks(make_pdf(""), "blank.pdf", Settings(data_dir=tmp_path))


def test_safe_filename_windows_path():
    assert safe_filename(r"C:\\Users\\Me\\report.pdf") == "report.pdf"
