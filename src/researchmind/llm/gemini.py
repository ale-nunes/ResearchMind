"""Small Google Gen AI SDK adapter with bounded retry/backoff."""

from __future__ import annotations

from functools import cached_property

from google import genai
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from researchmind.config import settings


def _is_retryable(exc: BaseException) -> bool:
    """Retry transient network failures and temporary API rate/server errors only."""
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return True
    status = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return status in {429, 500, 502, 503, 504}


class GeminiTextGenerator:
    """Generate text using the official Google Gen AI SDK."""

    def __init__(self, model: str | None = None) -> None:
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Add it to your local .env file; never commit it."
            )
        self.model = model or settings.gemini_model or "gemini-flash-latest"

    @cached_property
    def client(self) -> genai.Client:
        return genai.Client(api_key=settings.gemini_api_key)

    @retry(
        retry=retry_if_exception(_is_retryable),
        wait=wait_random_exponential(multiplier=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def generate(self, prompt: str) -> str:
        """Return generated text; retry only transient network exceptions."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        text = response.text
        if not text or not text.strip():
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()
