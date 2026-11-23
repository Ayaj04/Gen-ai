# Day 14 — S1/S2 verification

The Day 14 assignment repeats Day 13's requirements. This checkpoint verifies
the existing implementation and preserves the original measurement provenance;
it does not introduce a second cache or claim the previous live run is new.

## S1 — production safeguards

| Requirement | Implementation and evidence | Result |
| --- | --- | --- |
| Latency and tokens per request | [Telemetry middleware](../app/observability.py), integrated with [chat](../app/llm.py) and [RAG](../app/rag.py) | JSON latency plus provider-reported prompt/completion/total usage; zero for no provider call, unknown for unreported usage |
| Simple cache | [Response cache](../app/response_cache.py) used by `/ask` and `/chat` | 128 entries, 300-second TTL, LRU eviction; stateful agent bypasses cache |
| Input limits | [API validation](../app/main.py) and telemetry body guard | 3–500 character questions, 16,384 byte body limit, bounded search/top-k/thread IDs |
| One prompt-injection test | `test_prompt_injection_in_user_and_retrieved_text` in [production tests](../tests/test_production.py) | Pass; rejects explicit user override before provider call and discards poisoned evidence |
| README Production notes with numbers | [Production notes](../README.md#production-notes) | Real-Groq cache measurements and fresh local validation numbers, clearly distinguished |

## S2 — project showcase

| Requirement | Evidence | Result |
| --- | --- | --- |
| Problem statement | [The problem](../README.md#the-problem) | Beginner documentation-discovery and evidence-tracing problem explained |
| Mermaid architecture | [Architecture](../README.md#architecture) | UI, API, cache, retrieval, Groq, agent, sources, and request logs |
| Demo video link | [Watch/download demo](demo.webm?raw=true), [recording description](demo.md) | Actual 22.88-second local UI recording; bundled WebM exists |
| Results table | [Results](../README.md#results) | Dataset, recorded retrieval results, tests, deployment, and measured cache latency |
| Three resume bullets | [docs/resume.md](resume.md) | Exactly three bullets, with supporting evidence links |

## Verification run

Verified on 23 November 2026, Windows, Python 3.14.5:

```powershell
python -m ruff check .
python -m pytest -q
python -m eval.run_production_eval --output eval/day14_checks.json
```

- Ruff: all checks passed.
- Pytest: 36 passed; tests include cache hit/miss/expiry/LRU behavior, token
  accounting, concurrent request isolation, agent approval usage, limits,
  prompt-version cache isolation, and injection rejection.
- Fresh smoke check: 10 health requests returned HTTP 200, median 3.761 ms.
- A 501-character question returned HTTP 422 in 7.636 ms; an injection attempt
  returned HTTP 422 in 3.795 ms. All 12 requests used zero provider tokens.
- Raw fresh samples: [day14_checks.json](../eval/day14_checks.json).

The [original real-Groq samples](../eval/production_results.json) are retained
from Day 13: `/ask` 3,756.658 ms uncached versus 3.111 ms median for five hits;
`/chat` 6,722.022 ms uncached versus 2.695 ms median for five hits. The two
uncached calls used 2,679 tokens in total; cached repeats used zero new tokens.
These are small local samples, not production throughput or Render latency.

## Remaining boundaries

The injection guard is a heuristic, not a general security guarantee. Cache
and agent memory are process-local. No new Docker image, Render deployment,
or public runtime verification was performed for this documentation checkpoint.
The CI configuration targets Python 3.11; this verification ran locally on 3.14.5.
