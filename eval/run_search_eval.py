
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from app.chunking import build_chunks
from app.embed import embed_texts


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "eval" / "search_results.md"

QUESTIONS = [
    "What is FastAPI?",
    "How to create an API using FastAPI?",
    "How to handle requests and responses in FastAPI?",
    "How do I use path parameters in FastAPI?",
    "How do I validate a JSON request body using Pydantic?",
    "How can I deploy FastAPIGuide to AWS ECS using Terraform and a CI/CD pipeline?",
    "How do I validate query parameters in FastAPI?",
    "How can I return a 404 error for a missing record?",
    "How do I set a response status code in FastAPI?",
    "How do I control returned fields using a response model?",
]


def main():
    chunks = build_chunks()

    if not chunks:
        raise RuntimeError("No chunks available")

    # Embed the documents once, not once per question
    document_texts = [
        f"{chunk['title']}. {chunk['text']}"
        for chunk in chunks
    ]

    document_vectors = embed_texts(document_texts)
    question_vectors = embed_texts(QUESTIONS)

    scores = cosine_similarity(
        question_vectors,
        document_vectors,
    )

    lines = [
        "# Day 07 - Semantic Search Results",
        "",
        "Embedding model: all-MiniLM-L6-v2",
        "",
        "Higher cosine similarity means closer vectors.",
        "Similarity is not proof of factual relevance.",
        "",
        "| Q | Rank | Document Title | Page | Score | Source |",
        "|---|---|---|---|---|---|",
    ]

    for q_index, question in enumerate(QUESTIONS):
        ranked = sorted(
            enumerate(scores[q_index]),
            key=lambda item: item[1],
            reverse=True,
        )[:3]

        print(f"\nQ{q_index + 1}: {question}")

        for rank, (chunk_index, score) in enumerate(
            ranked, start=1
        ):
            chunk = chunks[chunk_index]

            print(
                f"  {rank}. {chunk['title']} "
                f"(score: {score:.4f})"
            )

            lines.append(
                f"| Q{q_index + 1} | {rank} | "
                f"{chunk['title']} | "
                f"{chunk['page']} | "
                f"{score:.4f} | "
                f"[Source]({chunk['source']}) |"
            )

    lines.extend([
        "",
        "## Manual Evaluation",
        "",
        "Review whether the retrieved chunks actually answer",
        "each question, not just whether they are similar.",
        "",
        "### Q6 - Known Dataset Limitation",
        "",
        "The current records do not cover the full AWS ECS,",
        "Terraform and CI/CD deployment workflow.",
        "Any returned chunks must be checked for relevance.",
        "",
        "## Observations",
        "",
        "- Best successful retrieval: [fill in]",
        "- Weakest retrieval: [fill in]",
        "- Irrelevant results: [fill in]",
        "- Improvements needed: [fill in]",
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
