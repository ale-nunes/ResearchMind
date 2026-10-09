"""Text chunking helpers."""

import hashlib
import re
from collections.abc import Iterable

from researchmind.rag.models import DocumentChunk


def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph boundaries where possible."""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_pages(
    pages: Iterable[tuple[int, str]],
    source: str,
    chunk_size: int = 1200,
    overlap: int = 180,
) -> list[DocumentChunk]:
    """Split page text into overlapping character windows with stable IDs."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    document_id = hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]
    chunks: list[DocumentChunk] = []
    step = chunk_size - overlap

    for page_number, raw_text in pages:
        text = normalize_text(raw_text)
        if not text:
            continue
        starts = range(0, len(text), step)
        for start in starts:
            fragment = text[start : start + chunk_size].strip()
            if not fragment:
                continue
            text_hash = hashlib.sha256(fragment.encode("utf-8")).hexdigest()
            chunk_id = hashlib.sha256(
                f"{document_id}:{page_number}:{start}:{text_hash}".encode()
            ).hexdigest()[:24]
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    source=source,
                    page=page_number,
                    text=fragment,
                    text_hash=text_hash,
                )
            )
            if start + chunk_size >= len(text):
                break
    return chunks
