"""Persistent ChromaDB storage for chunk text and embeddings."""

from pathlib import Path
from typing import Any, cast

import chromadb

from researchmind.rag.models import DocumentChunk, Evidence


class VectorStore:
    """Persist document chunks and query them using caller-provided vectors."""

    def __init__(self, path: str | Path, collection_name: str = "researchmind_chunks") -> None:
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.path))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        """Insert or update chunks. Chroma requires one vector per chunk."""
        if len(chunks) != len(embeddings):
            raise ValueError("Each chunk must have exactly one embedding.")
        if not chunks:
            return
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=cast(Any, embeddings),
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "source": chunk.source,
                    "page": chunk.page if chunk.page is not None else -1,
                    "text_hash": chunk.text_hash,
                }
                for chunk in chunks
            ],
        )

    def query(self, query_embedding: list[float], limit: int = 8) -> list[Evidence]:
        """Return nearest chunks with cosine distance converted to a similarity score."""
        result = cast(
            dict[str, Any],
            self.collection.query(
                query_embeddings=cast(Any, [query_embedding]),
                n_results=max(1, limit),
                include=["documents", "metadatas", "distances"],
            ),
        )
        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        evidence: list[Evidence] = []
        for chunk_id, text, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=False
        ):
            page_value = int(metadata.get("page", -1))
            page = page_value if page_value > 0 else None
            score = 1.0 - float(distance)
            source = str(metadata.get("source", "unknown"))
            citation = f"{source}, p. {page}" if page else source
            evidence.append(
                Evidence(
                    chunk_id=chunk_id,
                    source=source,
                    page=page,
                    text=text or "",
                    vector_score=score,
                    combined_score=score,
                    citation=citation,
                )
            )
        return evidence
