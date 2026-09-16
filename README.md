# HalluGuard

HalluGuard is a model-agnostic AI reliability layer that turns LLM output into atomic claims, retrieves evidence, verifies each claim, grounds corrections in evidence, and re-verifies corrections.

## Architecture

`LLM output → claims → evidence → verification → correction → re-verification`

The project exposes a FastAPI API and a Python SDK. The verification engine combines NLI, embedding similarity, and an optional LLM judge. Evidence is ranked by relevance, authority, freshness, corroboration, independence, and provenance, with explicit conflict detection.

## Features

- Model-agnostic adapters: Mock, OpenAI, Gemini, Llama-compatible, Mistral-compatible
- Atomic claim decomposition
- Evidence retrieval with source metadata
- Multi-signal verification: NLI + embeddings + optional judge
- Hallucination taxonomy: factual, entity, temporal, numerical, relational, citation, contextual, logical
- Severity: Low / Medium / High / Critical
- Evidence-grounded correction and independent re-verification
- `UNVERIFIED` when evidence is insufficient or conflicting
- Claim-level explainable reliability reports

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn halluguard.api:app --reload
```

Then POST to `/v1/verify`:

```json
{
  "prompt": "Who wrote Pride and Prejudice?",
  "response": "Pride and Prejudice was written by Charlotte Bronte.",
  "retrieval": "memory"
}
```

For deterministic demos, the in-memory retriever is populated with a small evidence corpus. For production, implement `EvidenceRetriever` against your search/index provider and configure an LLM adapter.

## Tests

```bash
pytest
```

## License

MIT
