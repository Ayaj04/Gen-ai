
from pathlib import Path

import chromadb

from app.chunking import build_chunks
from app.embed import embed_texts


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "chroma"
COLLECTION_NAME = "fastapiguide_chunks"


def get_collection():
    """Open the local persistent Chroma collection."""

    client = chromadb.PersistentClient(path=str(DB_PATH))

    return client.get_or_create_collection(
        name=COLLECTION_NAME
    )


def index_documents(chunk_size=120, overlap=25):
    """Embed and index all documentation chunks."""

    chunks = build_chunks(
        chunk_size=chunk_size,
        overlap=overlap,
    )

    if not chunks:
        raise RuntimeError("No documentation chunks found")

    collection = get_collection()

    # Rebuild this project's collection to avoid stale chunks
    old_ids = collection.get(include=[])["ids"]

    if old_ids:
        collection.delete(ids=old_ids)

    batch_size = 32

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        texts = [
            f"{chunk['title']}. {chunk['text']}"
            for chunk in batch
        ]

        vectors = embed_texts(texts)

        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["text"] for chunk in batch],
            embeddings=vectors,
            metadatas=[
                {
                    "title": chunk["title"],
                    "page": chunk["page"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                }
                for chunk in batch
            ],
        )

        print(f"Indexed {min(start + len(batch), len(chunks))} chunks")

    print("Chroma collection count:", collection.count())


def search_semantic(question, limit=5):
    """Find the closest documentation chunks."""

    if not question.strip():
        return []

    collection = get_collection()

    if collection.count() == 0:
        raise RuntimeError(
            "Chroma index is empty. Run python -m app.vectorstore"
        )

    query_vector = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(limit, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    hits = []

    for chunk_id, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "id": chunk_id,
            "title": metadata["title"],
            "page": metadata["page"],
            "source": metadata["source"],
            "text": text,
            "distance": round(float(distance), 4),
        })

    return hits


if __name__ == "__main__":
    index_documents()
