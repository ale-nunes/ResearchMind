"""Fetch and extract readable text from a public HTTP(S) URL."""

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def summarize_url(url: str, max_chars: int = 12000) -> dict[str, str]:
    """Extract page title and text; this is extraction, not LLM summarization."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Only absolute HTTP(S) URLs are supported.")
    if not 500 <= max_chars <= 30000:
        raise ValueError("max_chars must be between 500 and 30000.")
    response = requests.get(
        url, timeout=15, headers={"User-Agent": "ResearchMind/0.1 (research prototype)"}
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type:
        raise ValueError("URL did not return HTML content.")
    soup = BeautifulSoup(response.text, "html.parser")
    for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        element.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else parsed.netloc
    text = " ".join(soup.get_text(" ", strip=True).split())
    return {"url": url, "title": title, "text": text[:max_chars]}
