"""Local SQLite notes for persistent, user-controlled research memory."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


def _connect(database_path: str | Path) -> sqlite3.Connection:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.execute("""CREATE TABLE IF NOT EXISTS research_notes (
        note_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    return connection


def save_note(
    title: str, content: str, database_path: str | Path = ".local/researchmind.sqlite3"
) -> int:
    """Save a note locally and return its ID."""
    title, content = title.strip(), content.strip()
    if not title or not content:
        raise ValueError("Both title and content are required.")
    with _connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO research_notes(title, content, created_at) VALUES (?, ?, ?)",
            (title, content, datetime.now(UTC).isoformat()),
        )
        note_id = cursor.lastrowid
        if note_id is None:
            raise RuntimeError("Could not retrieve the saved note ID.")
        return note_id


def read_note(
    note_id: int, database_path: str | Path = ".local/researchmind.sqlite3"
) -> dict[str, str | int] | None:
    """Read a note by ID; return None when it does not exist."""
    with _connect(database_path) as connection:
        row = connection.execute(
            "SELECT note_id, title, content, created_at FROM research_notes WHERE note_id = ?",
            (note_id,),
        ).fetchone()
    if row is None:
        return None
    return {"note_id": row[0], "title": row[1], "content": row[2], "created_at": row[3]}
