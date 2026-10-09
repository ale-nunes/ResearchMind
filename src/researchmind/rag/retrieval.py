"""Hybrid retrieval and simple score fusion."""

from researchmind.rag.embeddings import EmbeddingService
from researchmind.rag.lexical_search import LexicalStore
from researchmind.rag.models import Evidence
from researchmind.rag.vector_store import VectorStore


class HybridRetriever:
    """Fuse semantic and keyword results with reciprocal-rank fusion."""

    def __init__(
        self,
        embeddings: EmbeddingService,
        vector_store: VectorStore,
        lexical_store: LexicalStore,
    ) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.lexical_store = lexical_store

    def search(self, query: str, limit: int = 8, candidate_limit: int = 12) -> list[Evidence]:
        """Return ranked evidence from both retrieval channels."""
        query_vector = self.embeddings.embed_text(query)
        vector_hits = self.vector_store.query(query_vector, limit=candidate_limit)
        keyword_hits = self.lexical_store.search(query, limit=candidate_limit)

        merged: dict[str, Evidence] = {}
        for rank, item in enumerate(vector_hits, start=1):
            merged[item.chunk_id] = item.model_copy(update={"combined_score": 1.0 / (60 + rank)})

        for rank, item in enumerate(keyword_hits, start=1):
            if item.chunk_id in merged:
                existing = merged[item.chunk_id]
                merged[item.chunk_id] = existing.model_copy(
                    update={
                        "keyword_score": item.keyword_score,
                        "combined_score": existing.combined_score + 1.0 / (60 + rank),
                    }
                )
            else:
                merged[item.chunk_id] = item.model_copy(
                    update={"combined_score": 1.0 / (60 + rank)}
                )

        return sorted(
            merged.values(),
            key=lambda evidence: evidence.combined_score,
            reverse=True,
        )[:limit]
