"""Tool adapter around the Phase 3 hybrid RAG retriever."""

from researchmind.config import settings
from researchmind.rag.embeddings import EmbeddingService
from researchmind.rag.lexical_search import LexicalStore
from researchmind.rag.retrieval import HybridRetriever
from researchmind.rag.vector_store import VectorStore


def search_documents(query: str, limit: int = 5) -> list[dict[str, object]]:
    """Search indexed local documents and return evidence with source/page citations."""
    if not query.strip():
        raise ValueError("Query cannot be empty.")
    if not 1 <= limit <= 10:
        raise ValueError("limit must be between 1 and 10.")
    embeddings = EmbeddingService()
    vectors = VectorStore(settings.chroma_dir)
    lexical = LexicalStore(settings.sqlite_path)
    retriever = HybridRetriever(embeddings, vectors, lexical)
    evidence = retriever.search(query, limit=limit)
    return [
        {
            "text": item.text,
            "source": item.source,
            "page": item.page,
            "score": item.combined_score,
            "citation": f"{item.source}, p. {item.page}" if item.page else item.source,
        }
        for item in evidence
    ]
