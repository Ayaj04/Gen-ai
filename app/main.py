
from app.smart_search import rank_records
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.records import (
    load_records,
    get_by_id,
    search as keyword_search,
)

app = FastAPI(
    title="FastAPIGuide",
    description="Learn FastAPI from official documentation",
)

questions = []


class QuestionIn(BaseModel):
    question: str = Field(min_length=3)


# 1. Health check
@app.get("/health")
def health():
    return {
        "status": "ok",
        "records": len(load_records()),
    }


# 2. List records
@app.get("/records")
def list_records(limit: int = Query(default=10, ge=1, le=100)):
    records = load_records()

    return {
        "total": len(records),
        "records": [
            {"id": i, **record}
            for i, record in enumerate(records[:limit], start=1)
        ],
    }


# 3. Get one record
@app.get("/records/{id}")
def get_record(id: int):
    record = get_by_id(id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )

    return {"id": id, **record}


# 4. Search records (basic version)
@app.get("/search")
def search_records(q: str = Query(min_length=1)):
    results = rank_records(
        q,
        load_records(),
        limit=5,
    )

    return {
        "query": q,
        "count": len(results),
        "results": results,
    }


# 5. Submit a question
@app.post("/questions", status_code=201)
def create_question(payload: QuestionIn):
    question_text = payload.question.strip()

    if not question_text:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be blank",
        )

    saved = {
        "id": len(questions) + 1,
        "question": question_text,
    }

    questions.append(saved)

    suggestions = rank_records(
        question_text,
        load_records(),
        limit=1,
    )

    return {
        "saved": saved,
        "suggested_record": suggestions[0] if suggestions else None,
    }
