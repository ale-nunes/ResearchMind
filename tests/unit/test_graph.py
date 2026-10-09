"""Offline tests for the LangGraph multi-agent workflow."""

import pytest

pytest.importorskip("langgraph")

from researchmind.graph import build_research_graph  # noqa: E402


class FakeGenerator:
    """Predictable LLM substitute; tests never call the Gemini API."""

    def __init__(self, critic_responses: list[str] | None = None) -> None:
        self.critic_responses = list(
            critic_responses
            or [
                "VERDICT: ACCEPT\nFEEDBACK: Evidence is sufficient.",
            ]
        )
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        if "You are the Planner" in prompt:
            return "1. Search the question. 2. Compare evidence."
        if "You are the Analyst" in prompt:
            return "The evidence supports the finding [source-a, p. 2]."
        if "You are the Critic" in prompt:
            return self.critic_responses.pop(0)
        if "You are the Writer" in prompt:
            return "## Findings\nEvidence supports the finding.\n\n## Sources\n- source-a, p. 2"
        raise AssertionError("Unexpected prompt type")


def _doc_search(query: str, limit: int) -> list[dict[str, object]]:
    assert query
    assert limit == 5
    return [
        {"text": "Evidence text", "source": "source-a", "page": 2, "citation": "source-a, p. 2"}
    ]


def _web_search(query: str, limit: int) -> list[dict[str, str]]:
    assert query
    assert limit == 5
    return [{"title": "Source A", "url": "https://example.com/a", "snippet": "Public evidence"}]


def test_graph_returns_report_when_critic_accepts() -> None:
    generator = FakeGenerator()
    graph = build_research_graph(
        generator, document_search=_doc_search, public_web_search=_web_search
    )
    result = graph.invoke(
        {"question": "What does the evidence show?", "research_mode": "documents_web"}
    )
    assert "Sources" in result["report"]
    assert result["iteration"] == 1
    assert result["verdict"] == "ACCEPT"
    assert len(result["evidence"]) == 2


def test_graph_stops_after_iteration_limit() -> None:
    generator = FakeGenerator(
        [
            "VERDICT: NEED_MORE_EVIDENCE\nFEEDBACK: Need another source.",
            "VERDICT: NEED_MORE_EVIDENCE\nFEEDBACK: Still insufficient.",
        ]
    )
    graph = build_research_graph(
        generator,
        document_search=_doc_search,
        public_web_search=_web_search,
        max_iterations=2,
    )
    result = graph.invoke({"question": "Compare evidence", "research_mode": "documents_web"})
    assert result["iteration"] == 2
    assert result["verdict"] == "NEED_MORE_EVIDENCE"
    assert "REVIEW LIMIT REACHED: True" in generator.calls[-1]


def test_graph_rejects_iteration_limit_over_three() -> None:
    generator = FakeGenerator()
    try:
        build_research_graph(generator, max_iterations=4)
    except ValueError as exc:
        assert "between 1 and 3" in str(exc)
    else:
        raise AssertionError("Expected invalid iteration limit to raise ValueError")
