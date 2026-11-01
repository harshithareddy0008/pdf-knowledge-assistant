"""Mocked RAG logic tests; no external API calls and no Chroma connection."""
from types import SimpleNamespace

from langchain_core.documents import Document

from backend.config import Settings
from backend.services.rag import NO_ANSWER, answer_question, index_file


class FakeStore:
    def __init__(self):
        self.docs = []
        self.ids = []

    def get(self, where=None, include=None, limit=None):
        ids = self.ids
        if where:
            ids = [id for id in ids if any(d.metadata.get("file_id") == where["file_id"] for d in self.docs)]
        return {"ids": ids[:limit] if limit else ids}

    def add_documents(self, docs, ids):
        self.docs.extend(docs)
        self.ids.extend(ids)

    def similarity_search(self, question, k):
        return self.docs[:k]


def test_no_document_returns_friendly_message():
    response = answer_question(FakeStore(), "What is AI?", Settings())
    assert response["sources"] == []
    assert "Upload a PDF" in response["answer"]


def test_duplicate_upload_does_not_index_again(monkeypatch):
    from backend.services import rag

    docs = [Document(page_content="Alpha test", metadata={"file": "demo.pdf", "file_id": "abcd", "page": 1})]
    monkeypatch.setattr(rag, "extract_chunks", lambda *args: ("abcd", 1, docs))
    store = FakeStore()
    first = index_file(store, b"pdf", "demo.pdf", Settings())
    second = index_file(store, b"pdf", "demo.pdf", Settings())
    assert first["status"] == "indexed"
    assert second["status"] == "already_indexed"
    assert len(store.docs) == 1


def test_answer_returns_source_metadata(monkeypatch):
    from backend.services import rag

    store = FakeStore()
    store.add_documents(
        [Document(page_content="Regression predicts numerical values.", metadata={"file": "ml.pdf", "page": 3, "file_id": "a"})],
        ids=["a0"],
    )

    class FakeClient:
        def __init__(self, **kwargs):
            self.models = SimpleNamespace(generate_content=lambda **kwargs: SimpleNamespace(text="Regression predicts numerical values [1]."))

    monkeypatch.setattr(rag.genai, "Client", FakeClient)
    result = answer_question(store, "What is regression?", Settings(gemini_api_key="dummy"))
    assert result["sources"][0]["file"] == "ml.pdf"
    assert result["sources"][0]["page"] == 3
    assert "[1]" in result["answer"]
    assert NO_ANSWER not in result["answer"]
