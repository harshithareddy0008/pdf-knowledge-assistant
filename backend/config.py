"""Typed settings loaded from environment or local .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    app_access_token: str = ""
    api_base_url: str = "http://127.0.0.1:8000"
    data_dir: Path = Path("./data")
    max_upload_mb: int = 8
    max_pdf_pages: int = 80
    max_files_per_request: int = 4
    top_k: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()
