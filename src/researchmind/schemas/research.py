"""Typed state contract for the multi-agent research graph."""

from typing import Literal, TypedDict

ResearchMode = Literal["documents_only", "documents_web"]


class ResearchState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""

    question: str
    research_mode: ResearchMode
    plan: str
    evidence: list[dict[str, object]]
    analysis: str
    critique: str
    verdict: str
    iteration: int
    max_iterations: int
    report: str
    errors: list[str]
