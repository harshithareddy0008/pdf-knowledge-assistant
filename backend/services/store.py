"""A separate Chroma collection per workspace; raw PDFs are not saved to disk."""
from langchain_chroma import Chroma

from backend.config import Settings
from backend.services.embeddings import GeminiEmbeddings


def make_store(workspace_id: str, settings: Settings) -> Chroma:
    db_dir = settings.data_dir / "chroma"
    db_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=f"pdf_{workspace_id}",
        embedding_function=GeminiEmbeddings(
            api_key=settings.gemini_api_key,
            model=settings.gemini_embedding_model,
        ),
        persist_directory=str(db_dir.resolve()),
    )


def list_documents(store: Chroma) -> list[dict]:
    records = store.get(include=["metadatas"])
    documents: dict[str, dict] = {}
    for metadata in records.get("metadatas") or []:
        if not metadata:
            continue
        file_id = metadata.get("file_id", "")
        if not file_id:
            continue
        entry = documents.setdefault(
            file_id,
            {"file": metadata.get("file", "document.pdf"), "file_id": file_id, "pages": 0, "chunks": 0, "_pages": set()},
        )
        entry["chunks"] += 1
        entry["_pages"].add(int(metadata.get("page", 1)))
    result = []
    for entry in documents.values():
        entry["pages"] = len(entry.pop("_pages"))
        result.append(entry)
    return sorted(result, key=lambda item: item["file"].lower())
