"""LangGraph orchestration for the ResearchMind multi-agent workflow."""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.runnables import RunnableLambda
from langgraph.graph import END, START, StateGraph

from researchmind.agents.nodes import (
    DocumentSearch,
    TextGenerator,
    WebSearch,
    make_analyst,
    make_critic,
    make_planner,
    make_retriever,
    make_writer,
)
from researchmind.config import settings
from researchmind.schemas import ResearchState
from researchmind.tools import search_documents, web_search


def build_research_graph(
    generator: TextGenerator,
    *,
    document_search: DocumentSearch | None = None,
    public_web_search: WebSearch | None = None,
    max_iterations: int | None = None,
) -> object:
    """Build a compiled graph; dependencies can be injected for offline tests."""
    iteration_limit = settings.max_research_iterations if max_iterations is None else max_iterations
    if not 1 <= iteration_limit <= 3:
        raise ValueError("max_iterations must be between 1 and 3.")

    retriever_node = make_retriever(
        document_search=document_search or _default_document_search(),
        public_web_search=public_web_search or _default_web_search(),
    )

    graph = StateGraph(ResearchState)
    graph.add_node(
        "planner",
        RunnableLambda(make_planner(generator)),
    )
    graph.add_node(
        "retriever",
        RunnableLambda(retriever_node),
    )
    graph.add_node(
        "analyst",
        RunnableLambda(make_analyst(generator)),
    )
    graph.add_node(
        "critic",
        RunnableLambda(make_critic(generator)),
    )
    graph.add_node(
        "writer",
        RunnableLambda(make_writer(generator)),
    )

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "analyst")
    graph.add_edge("analyst", "critic")
    graph.add_conditional_edges(
        "critic",
        _route_after_critic(iteration_limit),
        {"retriever": "retriever", "writer": "writer"},
    )
    graph.add_edge("writer", END)
    return graph.compile()


def _route_after_critic(limit: int) -> Callable[[ResearchState], str]:
    """Route to another retrieval cycle only while review budget remains."""

    def route(state: ResearchState) -> str:
        if state.get("verdict") == "ACCEPT" or state.get("iteration", 0) >= limit:
            return "writer"
        return "retriever"

    return route


def _default_document_search() -> DocumentSearch:
    return search_documents


def _default_web_search() -> WebSearch:
    return web_search
