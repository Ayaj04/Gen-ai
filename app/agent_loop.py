
import re

from app.rag import ask_question
from app.tools import http_status_explainer


def choose_tool(question: str):
    """Select a tool using a simple Python rule."""

    match = re.search(r"\b[1-5][0-9]{2}\b", question)

    if match:
        return "http_status_explainer", match.group()

    return "rag", None


def run_agent(question: str):
    """Execute the selected tool and return an answer."""

    tool_name, code = choose_tool(question)

    # Tool 1: Local HTTP status lookup
    if tool_name == "http_status_explainer":
        row = http_status_explainer(code)

        if "error" in row:
            answer = row["error"]
        else:
            answer = (
                f"HTTP {row['code']} - {row['name']}. "
                f"Meaning: {row['meaning']}. "
                f"Typical FastAPI cause: "
                f"{row['typical_fastapi_cause']}. "
                f"Fix: {row['fix_hint']}."
            )

        return {
            "tool_used": tool_name,
            "answer": answer,
            "status_code": code,
            "details": row,
            "citations": [],
        }

    # Tool 2: Day 08 RAG system
    rag_result = ask_question(question, top_k=3)

    return {
        "tool_used": "rag",
        "answer": rag_result["answer"],
        "status_code": None,
        "details": None,
        "citations": rag_result.get("citations", []),
    }


if __name__ == "__main__":
    question = input("Ask FastAPIGuide: ")
    result = run_agent(question)

    print("\nSelected tool:", result["tool_used"])
    print("Answer:", result["answer"])
