"""Command-line entry point for document ingestion."""

import argparse
import logging
from pathlib import Path

from researchmind.config import settings
from researchmind.rag.chunking import chunk_pages
from researchmind.rag.embeddings import EmbeddingService
from researchmind.rag.ingestion import read_source
from researchmind.rag.lexical_search import LexicalStore
from researchmind.rag.vector_store import VectorStore


def ingest_file(file_path: str) -> int:
    """Extract, chunk, embed, and index one source file."""
    source_path = Path(file_path).resolve()
    records = read_source(source_path)
    chunks = chunk_pages(
        records,
        source=source_path.name,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    if not chunks:
        raise ValueError("No text chunks were created from this source.")

    embedding_service = EmbeddingService()
    vector_store = VectorStore(settings.chroma_dir)
    lexical_store = LexicalStore(settings.sqlite_path)

    batch_size = 16
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        vectors = embedding_service.embed_texts([chunk.text for chunk in batch])
        vector_store.upsert(batch, vectors)
        lexical_store.upsert(batch)
        logging.info(
            "indexed_chunks=%d total_chunks=%d", min(start + len(batch), len(chunks)), len(chunks)
        )

    return len(chunks)


def main() -> None:
    """Parse CLI arguments and ingest a source document."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    parser = argparse.ArgumentParser(description="Ingest a PDF, TXT, or Markdown file.")
    parser.add_argument("file", help="Path to a PDF, TXT, or Markdown source file.")
    args = parser.parse_args()
    count = ingest_file(args.file)
    print(f"Indexed {count} chunks successfully.")


if __name__ == "__main__":
    main()
