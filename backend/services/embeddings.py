"""LangChain-compatible embedding adapter using Google's official google-genai SDK."""
from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings


class GeminiEmbeddings(Embeddings):
    """Embed texts in small batches; use different task types for docs and queries."""

    def __init__(self, api_key: str, model: str = "gemini-embedding-001") -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        if not texts:
            return []
        output: list[list[float]] = []
        for start in range(0, len(texts), 16):
            batch = texts[start : start + 16]
            response = self.client.models.embed_content(
                model=self.model,
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=768,
                ),
            )
            embeddings = response.embeddings or []
            if len(embeddings) != len(batch):
                raise RuntimeError("Gemini returned an unexpected number of embeddings.")
            for emb in embeddings:
                if not emb.values:
                    raise RuntimeError("Gemini returned an empty embedding.")
                output.append(list(emb.values))
        return output

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]
