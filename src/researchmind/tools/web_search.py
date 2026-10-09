"""Free web search adapter using DDGS; availability depends on the provider."""

from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Search the public web and return titles, URLs, and snippets."""
    if not query.strip():
        raise ValueError("Search query cannot be empty.")
    if not 1 <= max_results <= 10:
        raise ValueError("max_results must be between 1 and 10.")
    results: list[dict[str, str]] = []
    with DDGS() as client:
        for item in client.text(query, max_results=max_results):
            results.append(
                {
                    "title": str(item.get("title", "")),
                    "url": str(item.get("href", item.get("url", ""))),
                    "snippet": str(item.get("body", "")),
                }
            )
    return results
