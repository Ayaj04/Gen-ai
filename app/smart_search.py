
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank_records(
    query: str,
    records: list[dict],
    limit: int = 5,
) -> list[dict]:

    if not query.strip() or not records:
        return []

    # Convert record information into searchable text
    fields = ("page_title", "key_concept", "main_symbol")

    texts = [
        " ".join(str(record.get(field, "")) for field in fields)
        for record in records
    ]

    # Convert documents into TF-IDF vectors
    vectorizer = TfidfVectorizer(stop_words="english")
    record_vectors = vectorizer.fit_transform(texts)
    query_vector = vectorizer.transform([query])

    # Measure similarity
    similarities = cosine_similarity(
        query_vector, record_vectors
    ).ravel()

    # Rank records by score, highest first
    ranked = sorted(
        enumerate(similarities, start=1),
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        {
            "id": record_id,
            "score": round(float(score), 4),
            **records[record_id - 1],
        }
        for record_id, score in ranked
        if score > 0
    ][:limit]
