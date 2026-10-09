# Phase 5 — Multi-agent orchestration

## Workflow

`START → Planner → Retriever → Analyst → Critic → (Retriever | Writer) → END`

- **Planner:** turns the question into a short research plan.
- **Retriever:** calls the local hybrid document search and, when enabled, DDGS web search. It keeps provenance with each result and records source failures without discarding the other source's results.
- **Analyst:** synthesizes the retrieved evidence and distinguishes supported findings from gaps.
- **Critic:** checks answer coverage and evidence support. It requests another retrieval cycle only when the answer may improve.
- **Writer:** produces the final report and is instructed to use only citations present in the evidence.
- **Supervisor:** LangGraph edges and conditional routing coordinate the nodes and stop after at most three Critic reviews.

## Running locally

1. Install dependencies in the active virtual environment:

   ```powershell
   python -m pip install -e ".[dev]"
   ```

2. Copy `.env.example` to `.env` if you have not already done so, and set `GEMINI_API_KEY` locally. Never commit `.env`.
3. Optionally set `GEMINI_MODEL`; the code defaults to `gemini-flash-latest` when it is blank.
4. Run the tests:

   ```powershell
   python -m pytest -v
   ```

The graph tests inject a fake generator and fake search functions; they do not call Gemini or the web. Integration with a real API should be tested separately because the free-tier quota may be limited.

## Scope and limitations

This phase implements graph orchestration and agent nodes. The existing Streamlit shell is intentionally unchanged; wiring the graph into the interface belongs to the UI phase. Tool use is currently orchestrated by the Retriever node and the existing tool adapters, not by unconstrained model-generated code. The calculator remains a restricted AST evaluator. Retrieved text is untrusted input and cannot override the system instructions.
