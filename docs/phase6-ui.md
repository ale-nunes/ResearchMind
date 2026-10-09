# Phase 6 — Streamlit interface

## Included

- Research question form with input validation.
- Source mode selector: local documents only, or local documents plus web search.
- Research execution through the existing LangGraph workflow.
- Final report rendering, evidence details, workflow warnings, and Markdown download.
- Friendly user-facing errors with expandable technical diagnostics.
- Gemini credentials are read from the existing environment-based settings; the UI never asks users to paste an API key.

## Run locally

From the repository root with the project's virtual environment active:

```powershell
python -m streamlit run src/researchmind/ui/app.py
```

Ensure `.env` contains `GEMINI_API_KEY` and that the dependencies are installed. Never commit `.env`.

## Validation

After applying the patch, run:

```powershell
ruff check src tests
mypy src
pytest
```

Then open the local Streamlit URL printed in the terminal and run one small research question. A real request uses the Gemini API quota.
