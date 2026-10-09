"""SQLite FTS5 index for keyword retrieval."""

import sqlite3
from pathlib import Path

from researchmind.rag.models import DocumentChunk, Evidence


class LexicalStore:
    """Maintain a lightweight full-text search index."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
                    chunk_id UNINDEXED, source UNINDEXED, page UNINDEXED, text
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path, timeout=30)

    def upsert(self, chunks: list[DocumentChunk]) -> None:
        """Replace lexical entries for the provided stable chunk IDs."""
        with self._connect() as connection:
            for chunk in chunks:
                connection.execute("DELETE FROM chunk_fts WHERE chunk_id = ?", (chunk.chunk_id,))
                connection.execute(
                    "INSERT INTO chunk_fts (chunk_id, source, page, text) VALUES (?, ?, ?, ?)",
                    (chunk.chunk_id, chunk.source, chunk.page or -1, chunk.text),
                )

    def search(self, query: str, limit: int = 8) -> list[Evidence]:
        """Return keyword matches ordered by SQLite's BM25 rank."""
        terms = [term for term in query.split() if term.strip()]
        if not terms:
            return []
        # Quoting each token prevents user punctuation from becoming FTS syntax.
        match_query = " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms)
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT chunk_id, source, page, text, bm25(chunk_fts) AS rank
                    FROM chunk_fts
                    WHERE chunk_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                    """,
                    (match_query, max(1, limit)),
                ).fetchall()
        except sqlite3.OperationalError:
            return []

        results: list[Evidence] = []
        for chunk_id, source, page_value, text, rank in rows:
            page_number = int(page_value)
            page = page_number if page_number > 0 else None
            score = 1.0 / (1.0 + max(0.0, float(rank)))
            citation = f"{source}, p. {page}" if page else source
            results.append(
                Evidence(
                    chunk_id=chunk_id,
                    source=source,
                    page=page,
                    text=text,
                    keyword_score=score,
                    combined_score=score,
                    citation=citation,
                )
            )
        return results
