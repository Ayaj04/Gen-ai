# FastAPIGuide — resume bullets

- Built a FastAPI documentation tutor with Streamlit, ChromaDB semantic retrieval, Groq answers, citations, and 20 source-attributed Python examples; the recorded 15-question evaluation retrieved an expected page for 13 of 14 in-scope questions.
- Delivered a LangGraph approval workflow for HTTP-status lookup and RAG, packaged the API with Docker, deployed it publicly on Render, and automated Ruff, Pytest, and Docker builds through GitHub Actions.
- Implemented request-level latency/token logging, a 128-entry TTL/LRU answer cache, input limits, and prompt-injection regression tests; measured a 3.111 ms median for five cached `/ask` requests with zero additional provider tokens after a 3.757-second uncached request in a local smoke test.

Evidence: [live API](https://gen-fast-api.onrender.com/docs),
[recorded retrieval evaluation](../eval/eval_runs.json),
[Day 13 measurement samples](../eval/production_results.json),
and [demo recording](demo.webm?raw=true).
The latency sample is local and small; it is not a production throughput claim.
