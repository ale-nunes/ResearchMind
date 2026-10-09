# ResearchMind

A multi-agent research assistant that combines private-document retrieval (RAG), web research, evidence analysis, citation checking, and Markdown report generation.

> **Current status:** Phase 3 — document ingestion, chunking, Gemini embeddings, persistent cache, vector retrieval, and hybrid retrieval are implemented. Multi-agent orchestration is planned for later phases.

## Requirements

- Python 3.11+
- A Google AI Studio API key for embedding generation
- Review the current model availability and free-tier quota in Google AI Studio before ingestion. Image-based PDFs use local Tesseract OCR; OCR itself does not use Gemini API credits.

## Local setup

```powershell
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Add your API key only to your local `.env` file:

```dotenv
GEMINI_API_KEY=your_local_key
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_OUTPUT_DIMENSIONALITY=768
```

Never commit `.env` or the key. `.env.example` must contain placeholders only.

## Ingest a document

Put the new PDF in `data/raw/Doping Cerebral - Davi Calazans.pdf`, then run:

```powershell
python -m researchmind.rag.cli "data/raw/Doping Cerebral - Davi Calazans.pdf"
```

Alternatively, use the installed command:

```powershell
researchmind-ingest "data/raw/Doping Cerebral - Davi Calazans.pdf"
```

The command extracts selectable page text first and falls back to local OCR for image-based PDFs. For OCR, install the extra with `python -m pip install -e ".[dev,ocr]"` and install the Tesseract OCR application for Windows (including Portuguese language data). The command then creates overlapping chunks, generates embeddings one at a time, caches each embedding in SQLite, and writes to ChromaDB and SQLite FTS5. Re-running the same source reuses cached embeddings and upserts stable chunk IDs.

## Retrieval from Python

```python
from researchmind.config import settings
from researchmind.rag.embeddings import EmbeddingService
from researchmind.rag.lexical_search import LexicalStore
from researchmind.rag.retrieval import HybridRetriever
from researchmind.rag.vector_store import VectorStore

embeddings = EmbeddingService()
vectors = VectorStore(settings.chroma_dir)
keywords = LexicalStore(settings.sqlite_path)
retriever = HybridRetriever(embeddings, vectors, keywords)

for evidence in retriever.search("What is a confidence interval?", limit=5):
    print(evidence.citation)
    print(evidence.text)
```

## Data layout

- `.local/chroma/`: persistent vector index
- `.local/embedding_cache.sqlite3`: cached embedding vectors
- `.local/researchmind.sqlite3`: SQLite FTS5 index and later application data

Local artifacts and source PDFs are ignored by Git by default.

## Limitations in Phase 3

- OCR uses local Tesseract for image-based PDFs; OCR quality depends on scan resolution and installed language packs. Set `OCR_LANGUAGE=por+eng` for Portuguese/English pages.
- Embeddings are requested sequentially to keep quota usage conservative. The ingestion loop is resumable through the persistent cache.
- The initial chunker uses character windows with overlap. For this 22-page book, the corpus is much smaller than the previous textbook; embedding usage depends on extracted text/chunks, not the PDF file size. Keep the default chunk size/overlap initially to limit API calls.
- The current citation refers to the source filename and PDF page number. Mapping to printed book page numbers is not automatic.
- Gemini free-tier quotas vary by model and project. Check active limits in Google AI Studio.

## Quality checks

```powershell
ruff check .
ruff format --check .
mypy src
pytest
```

## License

MIT for this project's code. Ensure you have the rights needed to index and distribute any source documents; do not commit copyrighted source PDFs without permission.

## Phase 4 — Tool adapters

The project now includes standalone tools for hybrid document search, public-web search (DDGS), arithmetic-only calculation, HTML text extraction from a URL, and local SQLite notes. These are callable Python functions; they are **not yet connected to the LangGraph agents** (that belongs to Phase 5).

Examples:

```python
from researchmind.tools import python_calculator, save_note, read_note

print(python_calculator("(1200 * 0.15) + 40"))
note_id = save_note("Research question", "Follow up on the evidence in chapter 2.")
print(read_note(note_id))
```

Document search requires the Phase 3 index and a valid `GEMINI_API_KEY`, because the query is embedded before hybrid retrieval. Web search and URL extraction use public services and can fail due to provider/network restrictions. URL extraction returns cleaned page text; it does not call an LLM or summarize claims. Always treat web content as untrusted input and verify sources before relying on them.

Tests:

```powershell
python -m pytest
```


## Phase 5: multi-agent workflow

The LangGraph workflow coordinates a Planner, Retriever, Analyst, Critic, and Writer. The Critic can request additional retrieval, with a hard limit of three review cycles. See [`docs/phase5-agents.md`](docs/phase5-agents.md) for the workflow, local setup, tests, and current limitations.
