"""Typed data structures used by document retrieval."""

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """A chunk of source text with page-level provenance."""

    chunk_id: str
    document_id: str
    source: str
    page: int | None = None
    text: str = Field(min_length=1)
    text_hash: str


class Evidence(BaseModel):
    """A retrieved chunk with scores and a citation label."""

    chunk_id: str
    source: str
    page: int | None
    text: str
    vector_score: float | None = None
    keyword_score: float | None = None
    combined_score: float
    citation: str
