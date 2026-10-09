"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration."""

    gemini_api_key: str | None = None
    gemini_model: str = ""
    gemini_embedding_model: str = "gemini-embedding-2"
    app_env: str = "development"
    log_level: str = "INFO"
    data_dir: str = "data"
    chroma_dir: str = ".local/chroma"
    sqlite_path: str = ".local/researchmind.sqlite3"
    embedding_cache_path: str = ".local/embedding_cache.sqlite3"
    chunk_size: int = Field(default=1200, ge=200, le=5000)
    chunk_overlap: int = Field(default=180, ge=0, le=1000)
    embedding_output_dimensionality: int = Field(default=768, ge=128, le=3072)
    embedding_max_attempts: int = Field(default=5, ge=1, le=10)
    max_research_iterations: int = Field(default=3, ge=1, le=3)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
