# Security baseline

- Store secrets in environment variables locally and platform secrets in deployment.
- Never commit `.env`, API keys, source PDFs, indexes, or local databases.
- Validate all model-generated tool arguments.
- Calculator implementation must use a restricted AST; never use `eval` or `exec`.
- URL fetching must block localhost, private, link-local, and reserved IP ranges, including after redirects.
- Treat retrieved text as untrusted data, not instructions.
- Bound timeouts, response sizes, result counts, and graph iterations.
