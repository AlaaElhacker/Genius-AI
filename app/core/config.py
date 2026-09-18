from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    cohere_api_key: str = ""

    primary_llm: str = "gemini"
    fallback_llm: str = "cohere"

    embedding_provider: str = "cohere"

    chroma_dir: Path = Path("./data/chroma_db")
    upload_dir: Path = Path("./data/uploads")
    registry_path: Path = Path("./data/documents.json")

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5
    max_upload_mb: int = 25

    collection_name: str = "medical_research"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
