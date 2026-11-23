import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import requests
import streamlit as st

from ui.snippets import cited_snippets, load_snippets

ROOT = Path(__file__).resolve().parent.parent
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)
FEEDBACK_FILE = ROOT / "data" / "feedback.jsonl"

st.set_page_config(
    page_title="FastAPIGuide",
    page_icon="📚",
    layout="wide",
)

st.title("📚 FastAPIGuide")
st.caption("Ask questions using official FastAPI documentation")

# Keep conversation data during Streamlit reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

if "pending" not in st.session_state:
    st.session_state.pending = None


def call_api(endpoint, payload):
    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def add_assistant(answer, citations=None):
    st.session_state.messages.append({
        "id": str(uuid4()),
        "role": "assistant",
        "content": answer,
        "citations": citations or [],
    })


def save_feedback(message_id, rating):
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "message_id": message_id,
        "rating": "up" if rating == 1 else "down",
        "timestamp": datetime.now(UTC).isoformat(),
    }

    with FEEDBACK_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


chat_tab, snippet_tab = st.tabs([
    "💬 Documentation chat",
    "Snippet card",
])


with chat_tab:
    mode = st.radio(
        "Choose backend",
        ["/ask", "/agent"],
        horizontal=True,
    )

    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            for citation in message.get("citations", []):
                title = citation.get("title", "Documentation")
                source = citation.get("source", "")

                if source.startswith("https://"):
                    st.markdown(f"- [{title}]({source})")

            # Thumbs up/down on assistant answers
            if message["role"] == "assistant":
                message_id = message["id"]

                rating = st.feedback(
                    "thumbs",
                    key=f"feedback_{message_id}",
                )

                saved_key = f"saved_{message_id}"

                if (
                    rating is not None
                    and st.session_state.get(saved_key) != rating
                ):
                    save_feedback(message_id, rating)
                    st.session_state[saved_key] = rating

    # Handle the LangGraph approval step
    pending = st.session_state.pending

    if pending is not None:
        st.warning(
            f"Approval required: {pending.get('tool')}\n\n"
            f"Question: {pending.get('question')}"
        )

        col1, col2 = st.columns(2)
        decision = None

        if col1.button("Approve tool"):
            decision = True

        if col2.button("Reject tool"):
            decision = False

        if decision is not None:
            try:
                data = call_api("/agent", {
                    "thread_id": st.session_state.thread_id,
                    "approve": decision,
                })

                result = data.get("result", {})

                add_assistant(
                    result.get("answer", "No answer returned."),
                    result.get("citations", []),
                )

                st.session_state.pending = None
                st.rerun()

            except requests.RequestException as exc:
                st.error(f"Agent error: {exc}")

    question = st.chat_input(
        "Ask a FastAPI question...",
        disabled=st.session_state.pending is not None,
    )

    if question:
        st.session_state.messages.append({
            "role": "user",
            "content": question,
        })

        try:
            if mode == "/ask":
                data = call_api("/ask", {
                    "question": question,
                    "top_k": 3,
                })

                add_assistant(
                    data.get("answer", "No answer returned."),
                    data.get("citations", []),
                )

            else:
                data = call_api("/agent", {
                    "thread_id": st.session_state.thread_id,
                    "question": question,
                })

                if data.get("status") == "approval_required":
                    st.session_state.pending = data["approval"]
                else:
                    result = data.get("result", {})
                    add_assistant(
                        result.get("answer", "No answer returned."),
                        result.get("citations", []),
                    )

        except requests.RequestException as exc:
            add_assistant(f"Unable to contact the API: {exc}")

        st.rerun()


with snippet_tab:
    st.subheader("Snippet card")
    st.caption("Copy a runnable example from the official FastAPI tutorial.")

    latest_answer = next(
        (message for message in reversed(st.session_state.messages)
         if message["role"] == "assistant"),
        {},
    )
    citations = latest_answer.get("citations", [])

    try:
        snippets = load_snippets()
    except (OSError, ValueError):
        snippets = []
        st.error("Tutorial examples could not be loaded. Restart the app or restore data/snippets.json.")

    scope = st.radio(
        "Snippet source",
        ["Latest cited docs", "Browse tutorial examples"],
        index=0 if citations else 1,
        horizontal=True,
    )
    choices = cited_snippets(citations, snippets) if scope == "Latest cited docs" else snippets

    if scope == "Latest cited docs" and not choices:
        st.info(
            "No bundled Python example matches the latest answer's citations. "
            "Ask a FastAPI question in Documentation chat, or choose Browse tutorial examples."
        )
    elif choices:
        if scope == "Browse tutorial examples":
            st.info("Browsing tutorial examples. These are not citations from a chat answer.")
        selected = st.selectbox(
            "Documentation example",
            range(len(choices)),
            index=next((i for i, item in enumerate(choices)
                        if item["page"] == "handling-errors"), 0),
            format_func=lambda index: choices[index]["title"],
        )
        snippet = choices[selected]
        with st.container(border=True):
            st.markdown(f"### {snippet['title']}")
            st.caption(f"Source file: {snippet['source']}")
            st.code(snippet["code"], language="python")
            st.caption("Use the copy button in the top-right corner of the code block.")
            st.link_button("Open in docs", snippet["docs_url"])
            st.link_button("View source file", snippet["source_url"])
            st.download_button(
                "Download example",
                data=snippet["code"],
                file_name=f"{snippet['page']}.py",
                mime="text/x-python",
            )
            st.caption("Save as main.py, install the example's dependencies, then run: uvicorn main:app --reload")
            st.caption("Form/file examples need python-multipart; email fields may need email-validator.")
