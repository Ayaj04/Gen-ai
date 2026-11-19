
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.graph import agent_graph
from app.llm import ChatResponse, generate_answer
from app.rag import ask_question
from app.records import (
    get_by_id,
    load_records,
)
from app.smart_search import rank_records
from app.vectorstore import search_semantic

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


# 6. AI-powered chat
class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    prompt_version: Literal["v1", "v2"] = "v2"


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):

    try:
        return generate_answer(
            question=payload.question,
            prompt_version=payload.prompt_version,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to generate an LLM response",
        ) from exc


@app.get("/search/semantic")
def semantic_search_endpoint(
    q: str = Query(min_length=1),
    limit: int = Query(default=5, ge=1, le=10),
):
    try:
        hits = search_semantic(q, limit=limit)

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    return {
        "query": q,
        "count": len(hits),
        "results": hits,
    }



# Day 08 - RAG endpoint

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


class Citation(BaseModel):
    number: int
    title: str
    page: str
    source: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    try:
        return ask_question(
            question=payload.question,
            top_k=payload.top_k,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="RAG is unavailable. Check the "
                   "Chroma index and Groq configuration.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to generate an answer.",
        ) from exc


# Day 09 - LangGraph agent

class AgentRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=100)
    question: str | None = Field(default=None, min_length=3)
    approve: bool | None = None


@app.post("/agent")
def agent_endpoint(payload: AgentRequest):

    # Provide either a question or an approval decision.
    if (payload.question is None) == (payload.approve is None):
        raise HTTPException(
            status_code=400,
            detail="Provide either question or approve",
        )

    config = {
        "configurable": {
            "thread_id": payload.thread_id
        }
    }

    try:
        snapshot = agent_graph.get_state(config)
        pending = bool(snapshot.next)

        if payload.question is not None:
            if pending:
                raise HTTPException(
                    status_code=409,
                    detail="Resolve pending approval first",
                )

            result = agent_graph.invoke(
                {"question": payload.question},
                config=config,
            )

        else:
            if not pending:
                raise HTTPException(
                    status_code=409,
                    detail="No pending approval for this thread",
                )

            result = agent_graph.invoke(
                Command(resume=payload.approve),
                config=config,
            )

    except HTTPException:
        raise

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="Agent dependency unavailable",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed",
        ) from exc

    # Return the pending approval request
    if "__interrupt__" in result:
        return {
            "status": "approval_required",
            "thread_id": payload.thread_id,
            "approval": result["__interrupt__"][0].value,
        }

    return {
        "status": "completed",
        "thread_id": payload.thread_id,
        "result": result["result"],
        "memory_count": len(result.get("history", [])),
    }


