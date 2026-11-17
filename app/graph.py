
import operator
import re
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from app.agent_loop import choose_tool, run_agent


class AgentState(TypedDict, total=False):
    question: str
    resolved_question: str
    tool: str
    approved: bool
    result: dict
    history: Annotated[list[dict], operator.add]


# Node 1: Plan the action
def plan_node(state: AgentState):
    question = state["question"]
    history = state.get("history", [])

    # Simple memory-based follow-up handling
    if history:
        previous = history[-1]

        if (
            re.search(r"\b(it|that|previous)\b",
                      question, re.IGNORECASE)
            and previous.get("status_code")
        ):
            code = previous["status_code"]
            question = f"{question} (HTTP {code})"

    tool, _ = choose_tool(question)

    return {
        "resolved_question": question,
        "tool": tool,
    }


# Node 2: Ask the user for approval
def approval_node(state: AgentState):
    decision = interrupt({
        "message": "Approve this tool call?",
        "tool": state["tool"],
        "question": state["resolved_question"],
    })

    return {"approved": decision is True}


# Node 3: Execute the approved tool
def execute_node(state: AgentState):
    if state["approved"]:
        result = run_agent(state["resolved_question"])
    else:
        result = {
            "tool_used": "none",
            "answer": "Tool call was not approved.",
            "status_code": None,
            "details": None,
            "citations": [],
        }

    memory_entry = {
        "question": state["question"],
        "tool": result["tool_used"],
        "status_code": result["status_code"],
        "answer": result["answer"],
    }

    return {
        "result": result,
        "history": [memory_entry],
    }


# Build the graph
builder = StateGraph(AgentState)

builder.add_node("plan", plan_node)
builder.add_node("approval", approval_node)
builder.add_node("execute", execute_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "approval")
builder.add_edge("approval", "execute")
builder.add_edge("execute", END)

# Thread-scoped short-term memory
checkpointer = InMemorySaver()

agent_graph = builder.compile(checkpointer=checkpointer)
