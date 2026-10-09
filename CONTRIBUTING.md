# Contributing

## Workflow

1. Create a focused branch from `main`: `feat/<short-description>`, `fix/<short-description>`, or `docs/<short-description>`.
2. Keep changes small and typed.
3. Add or update tests.
4. Run `ruff check .`, `ruff format --check .`, `mypy src`, and `pytest`.
5. Open a pull request with the problem, solution, tests, and any security implications.

## Commit convention

Use semantic prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, or `ci:`.

## Security

Never commit API keys, `.env`, private documents, local databases, or logs containing sensitive content. Report security issues privately to the repository maintainer.
