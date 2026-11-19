
import json
import time
from pathlib import Path

from app.rag import ask_question
from app.vectorstore import index_documents, search_semantic

ROOT = Path(__file__).resolve().parent.parent
EVAL_FILE = ROOT / "eval" / "eval_set.json"
OUTPUT_FILE = ROOT / "eval" / "eval_runs.json"

CONFIGS = [
    {
        "name": "A",
        "chunk_size": 120,
        "overlap": 25,
        "top_k": 3,
    },
    {
        "name": "B",
        "chunk_size": 200,
        "overlap": 40,
        "top_k": 5,
    },
]


def main():
    cases = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    assert len(cases) == 15, "Evaluation set must have 15 rows"

    summaries = []
    all_results = []

    for config in CONFIGS:
        print(f"\nTesting configuration {config['name']}")

        # Rebuild Chroma using this configuration.
        index_documents(
            chunk_size=config["chunk_size"],
            overlap=config["overlap"],
        )

        retrieval_hits = 0
        cited_answers = 0
        q6_pass = False

        for case in cases:
            question = case["question"]
            expected = set(case["expected_pages"])

            hits = search_semantic(
                question,
                limit=config["top_k"],
            )

            retrieved_pages = [hit["page"] for hit in hits]

            # Retrieval hit: Did we retrieve an expected page?
            hit = bool(expected.intersection(retrieved_pages))

            if not case["should_abstain"] and hit:
                retrieval_hits += 1

            # Test the generated RAG answer.
            answer = ask_question(
                question,
                top_k=config["top_k"],
            )

            refused = answer["answer"].startswith("I don't know")

            valid_sources = {
                hit["source"] for hit in hits
            }

            valid_citations = (
                bool(answer["citations"])
                and all(
                    citation["source"] in valid_sources
                    for citation in answer["citations"]
                )
            )

            if (
                not case["should_abstain"]
                and not refused
                and valid_citations
            ):
                cited_answers += 1

            if case["id"] == "Q6":
                q6_pass = refused

            all_results.append({
                "config": config["name"],
                "question_id": case["id"],
                "question": question,
                "retrieved_pages": retrieved_pages,
                "retrieval_hit": hit,
                "answer": answer,
                "refused": refused,
                "valid_citations": valid_citations,
            })

            print(
                f"{case['id']}: "
                f"retrieval={'hit' if hit else 'miss'}, "
                f"refused={refused}"
            )

            # Gentle pacing for provider rate limits.
            time.sleep(1)

        summaries.append({
            **config,
            "retrieval_hits": retrieval_hits,
            "cited_answers": cited_answers,
            "q6_pass": q6_pass,
        })

    # Select by retrieval coverage, then cited-answer count.
    # A failed Q6 refusal disqualifies a configuration.
    eligible = [s for s in summaries if s["q6_pass"]]

    if not eligible:
        raise RuntimeError("Neither configuration passed Q6")

    winner = max(
        eligible,
        key=lambda s: (
            s["retrieval_hits"],
            s["cited_answers"],
        ),
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            {
                "summaries": summaries,
                "winner": winner,
                "results": all_results,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nCONFIGURATION RESULTS")
    print("Config | Retrieval hits/14 | Cited answers/14 | Q6")
    for summary in summaries:
        print(
            f"{summary['name']} | "
            f"{summary['retrieval_hits']}/14 | "
            f"{summary['cited_answers']}/14 | "
            f"{'Pass' if summary['q6_pass'] else 'Fail'}"
        )

    print(f"\nProvisional winner: {winner['name']}")
    print(f"Detailed results saved to {OUTPUT_FILE}")

    # Leave the persistent database indexed with the winner.
    index_documents(
        chunk_size=winner["chunk_size"],
        overlap=winner["overlap"],
    )


if __name__ == "__main__":
    main()
