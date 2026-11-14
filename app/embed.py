
import os
from functools import lru_cache

# Reduce numerical library thread usage
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model():
    """Load the embedding model once per Python process."""
    return SentenceTransformer(MODEL_NAME, device="cpu")


def embed_texts(texts):
    """Return normalized embedding vectors."""

    if not texts:
        return []

    embeddings = get_model().encode(
        texts,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()


if __name__ == "__main__":
    vectors = embed_texts([
        "How do I handle errors in FastAPI?",
        "How can I return an HTTP 404 response?",
    ])

    print("Number of vectors:", len(vectors))
    print("Dimensions:", len(vectors[0]))
