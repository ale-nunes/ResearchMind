"""Public tool API with lazy imports so lightweight tools need no network SDKs."""

from researchmind.tools.calculator import python_calculator
from researchmind.tools.notes import read_note, save_note


def search_documents(query: str, limit: int = 5) -> list[dict[str, object]]:
    """Search indexed local documents; imports the retrieval stack on demand."""
    from researchmind.tools.document_search import search_documents as implementation

    return implementation(query, limit)


def web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Search the public web; imports the search provider on demand."""
    from researchmind.tools.web_search import web_search as implementation

    return implementation(query, max_results)


def summarize_url(url: str, max_chars: int = 12000) -> dict[str, str]:
    """Extract text from a public HTML URL; imports HTTP dependencies on demand."""
    from researchmind.tools.url_summary import summarize_url as implementation

    return implementation(url, max_chars)


__all__ = [
    "python_calculator",
    "read_note",
    "save_note",
    "search_documents",
    "summarize_url",
    "web_search",
]
