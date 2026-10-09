# Phase 4 — Tool adapters

## Implemented

- `search_documents(query, limit=5)`: calls the Phase 3 hybrid retriever and returns evidence with source/page citation fields.
- `web_search(query, max_results=5)`: free DDGS search adapter; provider availability and throttling are outside this application's control.
- `python_calculator(expression)`: arithmetic-only AST evaluator; it rejects function calls, names, attributes, and oversized expressions.
- `summarize_url(url, max_chars=12000)`: validates HTTP(S), downloads HTML with a timeout, removes common navigation/script elements, and returns extracted text. Despite its name, this is extraction, not LLM summarization.
- `save_note(title, content)` / `read_note(note_id)`: local SQLite note storage with parameterized SQL.

## Deliberate scope boundary

These functions are independent adapters. They are not yet exposed to a model through function calling and are not wired into LangGraph. That orchestration belongs to Phase 5. Do not pass secrets or private URLs to web tools. Web results are untrusted data and need source validation.

## Quick manual checks

```python
from researchmind.tools import python_calculator, web_search, save_note, read_note

print(python_calculator("(15 + 5) / 2"))
print(web_search("official Gemini API documentation", max_results=3))
note_id = save_note("Test note", "A local note")
print(read_note(note_id))
```
