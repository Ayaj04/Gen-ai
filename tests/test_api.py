
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



def fake_ask_question(*args, **kwargs):
    return {
        "answer": "Use HTTPException to handle errors in FastAPI.",
        "citations": [
            {
                "number": 1,
                "page": "Handling Errors",
                "title": "Handling Errors - FastAPI",
                "source": "https://fastapi.tiangolo.com/tutorial/handling-errors/"
            }
        ]
    }


def test_ask_endpoint(client, monkeypatch):
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
    assert len(data["citations"]) == 1
    assert data["citations"][0]["title"] == "Handling Errors - FastAPI"

