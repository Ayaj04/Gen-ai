
from langgraph.types import Command

from app.graph import agent_graph


config = {
    "configurable": {
        "thread_id": "day09-test"
    }
}

# First request: should pause for approval
result = agent_graph.invoke(
    {"question": "What does HTTP 404 mean?"},
    config=config,
)

print("Approval request:")
print(result["__interrupt__"][0].value)

# Approve and resume the same thread
result = agent_graph.invoke(
    Command(resume=True),
    config=config,
)

print("\nAgent answer:")
print(result["result"]["answer"])

# Test conversation memory
result = agent_graph.invoke(
    {"question": "How do I fix it?"},
    config=config,
)

print("\nFollow-up approval:")
print(result["__interrupt__"][0].value)

result = agent_graph.invoke(
    Command(resume=True),
    config=config,
)

print("\nFollow-up answer:")
print(result["result"]["answer"])
print("Memory entries:", len(result["history"]))
