
import os
from functools import lru_cache

# Reduce numerical library thread usage
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

MODEL_NAME = "all-MiniLM-L6-v2 (Chroma ONNX)"


@lru_cache(maxsize=1)
def get_model():
    """Create Chroma's ONNX MiniLM embedder once, on first use."""
    from chromadb.utils.embedding_functions import (
        DefaultEmbeddingFunction,
    )

    return DefaultEmbeddingFunction()


def embed_texts(texts):
    """Return normalized embedding vectors."""

    if not texts:
        return []

    embeddings = get_model()(texts)

    return [embedding.tolist() for embedding in embeddings]


if __name__ == "__main__":
    vectors = embed_texts([
        "How do I handle errors in FastAPI?",
        "How can I return an HTTP 404 response?",
    ])

    print("Number of vectors:", len(vectors))
    print("Dimensions:", len(vectors[0]))
