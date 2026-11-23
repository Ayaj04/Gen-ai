def test_semantic_search_builds_missing_index_on_demand(monkeypatch):
    from app import embed, vectorstore

    state = {"built": False, "build_calls": 0}

    class Collection:
        def count(self):
            return 1 if state["built"] else 0

        def query(self, **kwargs):
            assert kwargs["query_embeddings"] == [[0.1, 0.2]]
            return {
                "ids": [["handling-errors-0000"]],
                "documents": [["Use HTTPException."]],
                "metadatas": [[{
                    "title": "Handling Errors",
                    "page": "handling-errors",
                    "source": "https://fastapi.tiangolo.com/",
                }]],
                "distances": [[0.1]],
            }

    collection = Collection()

    def fake_index_documents():
        state["built"] = True
        state["build_calls"] += 1

    monkeypatch.setattr(
        vectorstore,
        "get_collection",
        lambda: collection,
    )
    monkeypatch.setattr(
        vectorstore,
        "index_documents",
        fake_index_documents,
    )
    monkeypatch.setattr(
        embed,
        "embed_texts",
        lambda texts: [[0.1, 0.2]],
    )

    hits = vectorstore.search_semantic("How do I handle errors?", limit=1)

    assert state["build_calls"] == 1
    assert hits[0]["page"] == "handling-errors"
