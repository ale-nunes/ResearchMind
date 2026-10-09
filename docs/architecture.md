# Architecture decisions

- LangGraph will own workflow state and routing in a later phase; Gemini API calls use `google-genai`.
- Pydantic validates structured data contracts.
- ChromaDB persists semantic vectors; SQLite FTS5 supplies keyword retrieval.
- Embedding vectors are cached in SQLite using a key that includes model, dimensions, and text.
- The local index, cache, and database live under `.local/`, which is ignored by Git.
- `gemini-embedding-2` is the configured embedding model; changing models requires re-embedding the corpus.
- Retrieved text is untrusted data and must never override system instructions.


## OCR for image-based PDFs

The ingestion layer first tries selectable PDF text. If every page is empty, it renders pages locally with PyMuPDF and calls Tesseract through pytesseract. This avoids sending page images to Gemini. Tesseract must be installed separately on the machine, with Portuguese language data enabled.

## Phase 5 — agent workflow

- LangGraph coordinates Planner → Retriever → Analyst → Critic → Writer.
- The Critic may request another retrieval cycle, but the configured maximum is capped at three reviews.
- Gemini text generation uses the official `google-genai` SDK; `gemini-flash-latest` is the fallback model when `GEMINI_MODEL` is blank.
- Graph nodes accept injected generator/search functions so tests run without API calls or network access.
- The Streamlit UI remains a scaffold in this phase; UI integration is reserved for the UI phase.
