"""Smoke test the Gemini generation and embedding models (makes live API requests)."""
from google import genai
from google.genai import types

from backend.config import get_settings


def main() -> None:
    s = get_settings()
    if not s.gemini_api_key or s.gemini_api_key.startswith("PASTE_"):
        raise SystemExit("Set your real GEMINI_API_KEY in .env first.")
    client = genai.Client(api_key=s.gemini_api_key)
    print("Testing generation model:", s.gemini_model)
    response = client.models.generate_content(model=s.gemini_model, contents="Reply with only: READY")
    print("Generation:", response.text)
    print("Testing embedding model:", s.gemini_embedding_model)
    vectors = client.models.embed_content(
        model=s.gemini_embedding_model,
        contents=["Hello world"],
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768),
    )
    print("Embedding dimensions:", len(vectors.embeddings[0].values))
    print("Gemini generation and embeddings are working!")


if __name__ == "__main__":
    main()
