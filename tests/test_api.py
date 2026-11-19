
def test_records_limit(client):
    response = client.get("/records?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "total" in data
    assert "records" in data
    assert len(data["records"]) == 2


def test_records_limit(client):
    response = client.get("/records?limit=2")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "total" in data
    assert "records" in data
    assert len(data["records"]) == 2


def test_missing_record_returns_404(client):
    response = client.get("/records/999999")

    assert response.status_code == 404


def fake_ask_question(question, top_k=3):
    return {
        "answer": "FastAPI uses HTTPException for HTTP errors.",
        "citations": [
            {
                "number": 1,
                "page": "Handling Errors",
                "title": "Handling Errors",
                "source": (
                    "https://fastapi.tiangolo.com/tutorial/"
                    "handling-errors/"
                ),
            }
        ],
    }

    # Replace the function used by the /ask endpoint.

    monkeypatch.setattr(
        "app.main.ask_question",
        fake_ask_question,
    )

    response = client.post(
        "/ask",
        json={
            "question": "How do I handle errors?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "HTTPException" in data["answer"]
    assert len(data["citations"]) > 0
