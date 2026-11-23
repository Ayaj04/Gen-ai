
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel

from records import load_records

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")


class ChatResponse(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    follow_up: str


def read_prompt(filename: str) -> str:
    path = ROOT / "prompts" / filename
    return path.read_text(encoding="utf-8")


def generate_answer(
    question: str,
    prompt_version: Literal["v1", "v2"] = "v2",
) -> ChatResponse:
    from groq import Groq

    from app.smart_search import rank_records

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    # Read system and task prompts
    system_prompt = read_prompt("system.txt")
    task_prompt = read_prompt(f"task_{prompt_version}.txt")

    # Retrieve relevant official documentation records
    records = load_records()
    matches = rank_records(question, records, limit=3)

    if not matches:
        return ChatResponse(
            answer="The available documentation does not "
                   "contain enough information to answer this question.",
            confidence="low",
            follow_up="Could you ask about a topic covered "
                      "by the FastAPI tutorial?",
        )

    context_parts = []

    for record in matches:
        context_parts.append(
            f"Page: {record['page_title']}\n"
            f"Concept: {record['key_concept']}\n"
            f"Main symbol: {record['main_symbol']}\n"
            f"Example: {record['example_response'][:700]}\n"
            f"Source: {record['source_url']}"
        )

    context = "\n\n".join(context_parts)

    user_message = (
        f"{task_prompt}\n\n"
        f"USER QUESTION:\n{question}\n\n"
        f"RETRIEVED DOCUMENTATION:\n{context}"
    )

    client = Groq(api_key=api_key, timeout=30.0)

    completion = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    result = completion.choices[0].message.content

    if not result:
        raise ValueError("LLM returned an empty response")

    # Parse JSON and validate the three required fields
    return ChatResponse.model_validate_json(result)
