
import os
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import AfterValidator, BaseModel, Field, StringConstraints

from app.llm import ChatResponse
from app.observability import RequestTelemetryMiddleware
from app.records import (
    get_by_id,
    load_records,
)
from app.response_cache import response_cache
from app.safety import validate_question

QuestionText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500),
    AfterValidator(validate_question),
]
SearchText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


def rank_records(*args, **kwargs):
    """Load scikit-learn only when a text search is requested."""
    from app.smart_search import rank_records as rank_records_impl

    return rank_records_impl(*args, **kwargs)


def generate_answer(*args, **kwargs):
    """Load chat dependencies only when the chat endpoint is used."""
    from app.llm import generate_answer as generate_answer_impl

    return generate_answer_impl(*args, **kwargs)


def search_semantic(*args, **kwargs):
    """Load Chroma and the embedding stack on first semantic search."""
    from app.vectorstore import search_semantic as search_semantic_impl

    return search_semantic_impl(*args, **kwargs)


def ask_question(*args, **kwargs):
    """Load retrieval and LLM dependencies only for a RAG request."""
    from app.rag import ask_question as ask_question_impl

    return ask_question_impl(*args, **kwargs)


@lru_cache(maxsize=1)
def get_agent_graph():
    """Build the stateful LangGraph workflow only when it is needed."""
    from app.graph import agent_graph

    return agent_graph

app = FastAPI(
    title="FastAPIGuide",
    description="Learn FastAPI from official documentation",
)
app.add_middleware(RequestTelemetryMiddleware)

questions = []


class QuestionIn(BaseModel):
    question: QuestionText

@app.get("/")
def root():
    return {"message" : "Welcome to my website"}

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
def search_records(q: Annotated[SearchText, Query()]):
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
    question: QuestionText
    prompt_version: Literal["v1", "v2"] = "v2"


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):

    try:
        return response_cache.get_or_compute(
            ("chat", payload.question, payload.prompt_version, os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")),
            lambda: ChatResponse.model_validate(generate_answer(
                question=payload.question, prompt_version=payload.prompt_version,
            )).model_dump(),
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
    q: Annotated[SearchText, Query()],
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
    question: QuestionText
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
        return response_cache.get_or_compute(
            ("ask", payload.question, payload.top_k, os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")),
            lambda: AskResponse.model_validate(ask_question(
                question=payload.question, top_k=payload.top_k,
            )).model_dump(),
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
    thread_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    question: QuestionText | None = None
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
        agent_graph = get_agent_graph()
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

            from langgraph.types import Command

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


