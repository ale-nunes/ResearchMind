
"""Evaluation tests for evidence retrieval and failure handling."""

from __future__ import annotations

from researchmind.agents.nodes import make_retriever


def test_retriever_returns_document_evidence() -> None:
    """Document results should be marked and preserved as evidence."""

    def document_search(query: str, limit: int) -> list[dict[str, object]]:
        assert query
        assert limit == 5
        return [
            {
                "text": "Solar energy is renewable.",
                "citation": "documento_teste.txt, p. 1",
            }
        ]

    def web_search(query: str, limit: int) -> list[dict[str, str]]:
        return []

    retriever = make_retriever(document_search, web_search)
    result = retriever(
        {"question": "What is solar energy?", "research_mode": "documents_only"}
    )

    assert len(result["evidence"]) == 1
    assert result["evidence"][0]["kind"] == "document"
    assert result["evidence"][0]["citation"] == "documento_teste.txt, p. 1"
    assert result["errors"] == []


def test_retriever_records_document_search_failure() -> None:
    """Document search failures should be recorded instead of propagated."""

    def failing_document_search(
        query: str, limit: int
    ) -> list[dict[str, object]]:
        raise RuntimeError("simulated document search failure")

    def web_search(query: str, limit: int) -> list[dict[str, str]]:
        return []

    retriever = make_retriever(failing_document_search, web_search)
    result = retriever(
        {"question": "What is solar energy?", "research_mode": "documents_only"}
    )

    assert result["evidence"] == []
    assert len(result["errors"]) == 1
    assert "Document retrieval failed" in result["errors"][0]
    assert "simulated document search failure" in result["errors"][0]


def test_retriever_searches_web_in_documents_web_mode() -> None:
    """Combined mode should retrieve web evidence as well as documents."""

    document_calls = 0

    def document_search(query: str, limit: int) -> list[dict[str, object]]:
        nonlocal document_calls
        document_calls += 1
        return [{"text": "Local evidence", "citation": "local.txt, p. 1"}]

    def web_search(query: str, limit: int) -> list[dict[str, str]]:
        assert query == "Compare solar energy"
        assert limit == 5
        return [
            {
                "title": "Public source",
                "url": "https://example.com/solar",
                "snippet": "Web evidence",
            }
        ]

    retriever = make_retriever(document_search, web_search)
    result = retriever(
        {
            "question": "Compare solar energy",
            "research_mode": "documents_web",
        }
    )

    assert any(item.get("kind") == "web" for item in result["evidence"])
    assert document_calls == 1
