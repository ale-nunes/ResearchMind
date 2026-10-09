"""Gemini embeddings with persistent SQLite caching and bounded retries."""

import hashlib
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

from google import genai
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from researchmind.config import settings

logger = logging.getLogger(__name__)


def _is_retryable(error: BaseException) -> bool:
    """Retry likely transient rate-limit or server errors, not invalid requests."""
    message = str(error).lower()
    retry_markers = (
        "429",
        "resource_exhausted",
        "rate limit",
        "503",
        "502",
        "500",
        "temporarily unavailable",
        "deadline",
        "timeout",
    )
    return any(marker in message for marker in retry_markers)


class EmbeddingService:
    """Create and cache embeddings from the official Google Gen AI SDK."""

    def __init__(
        self,
        cache_path: str | Path | None = None,
        model: str | None = None,
        api_key: str | None = None,
        output_dimensionality: int | None = None,
    ) -> None:
        resolved_key = api_key or settings.gemini_api_key
        if not resolved_key:
            raise ValueError("GEMINI_API_KEY is missing. Set it in your local .env file.")
        self.model = model or settings.gemini_embedding_model
        self.output_dimensionality = (
            output_dimensionality or settings.embedding_output_dimensionality
        )
        self.client = genai.Client(api_key=resolved_key)
        self.cache_path = Path(cache_path or settings.embedding_cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_cache()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.cache_path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_cache(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS embedding_cache (
                    cache_key TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    dimensions INTEGER NOT NULL,
                    vector TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def _cache_key(self, text: str) -> str:
        raw = f"{self.model}:{self.output_dimensionality}:{text}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _get_cached(self, key: str) -> list[float] | None:
        import json

        with self._connect() as connection:
            row = connection.execute(
                "SELECT vector FROM embedding_cache WHERE cache_key = ?", (key,)
            ).fetchone()
        return json.loads(row["vector"]) if row else None

    def _save_cached(self, key: str, vector: list[float]) -> None:
        import json

        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO embedding_cache
                (cache_key, model, dimensions, vector, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    key,
                    self.model,
                    len(vector),
                    json.dumps(vector, separators=(",", ":")),
                    time.time(),
                ),
            )

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_random_exponential(multiplier=1, max=30),
        stop=stop_after_attempt(settings.embedding_max_attempts),
        reraise=True,
    )
    def _request_embedding(self, text: str) -> list[float]:
        """Call the Gemini embedding endpoint with retry on transient failures."""
        response: Any = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config={"output_dimensionality": self.output_dimensionality},
        )
        if not response.embeddings or not response.embeddings[0].values:
            raise RuntimeError("Gemini returned an empty embedding.")
        return [float(value) for value in response.embeddings[0].values]

    def embed_text(self, text: str) -> list[float]:
        """Return a cached vector or generate and cache a new one."""
        if not text.strip():
            raise ValueError("Cannot embed empty text.")
        key = self._cache_key(text)
        cached = self._get_cached(key)
        if cached is not None:
            return cached
        vector = self._request_embedding(text)
        self._save_cached(key, vector)
        logger.info("embedding_created model=%s dimensions=%d", self.model, len(vector))
        return vector

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed sequentially to respect quotas and reuse cache entries."""
        return [self.embed_text(text) for text in texts]
