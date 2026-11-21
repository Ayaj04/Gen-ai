import csv
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import requests
import streamlit as st

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


chat_tab, profile_tab = st.tabs([
    "💬 Documentation chat",
    "🧩 Profile chips",
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


with profile_tab:
    st.subheader("Find schemes for your profile")
    st.caption(
        "Profile matching is a preliminary filter, "
        "not a final eligibility decision."
    )

    age = st.pills(
        "Age band",
        ["Below 18", "18-25", "26-40", "41-60", "60+"],
    )

    gender = st.pills(
        "Gender",
        ["Female", "Male", "Other"],
    )

    occupation = st.pills(
        "Occupation",
        [
            "Student", "Farmer", "Self-employed",
            "Employed", "Unemployed", "Other",
        ],
    )

    income = st.pills(
        "Annual income band",
        ["Below 2 lakh", "2-5 lakh", "Above 5 lakh"],
    )

    category = st.pills(
        "Category",
        ["General", "OBC", "SC", "ST", "Other"],
    )

    residence = st.pills(
        "Area",
        ["Rural", "Urban"],
    )

    profile = {
        "age_band": age,
        "gender": gender,
        "occupation": occupation,
        "income_band": income,
        "category": category,
        "residence": residence,
    }

    schemes_file = ROOT / "data" / "schemes.csv"

    if schemes_file.exists():
        with schemes_file.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            schemes = list(csv.DictReader(file))
    else:
        schemes = []

    st.divider()
    st.subheader("Matching scheme cards")

    match_count = 0

    for scheme in schemes:
        reasons = []
        matches = True

        for field, selected in profile.items():
            if selected is None:
                continue

            allowed = {
                value.strip().lower()
                for value in scheme.get(field, "").split("|")
                if value.strip()
            }

            if (
                selected.lower() not in allowed
                and "any" not in allowed
            ):
                matches = False
                break

            reasons.append(f"{field}: {selected}")

        if not matches:
            continue

        match_count += 1

        with st.container(border=True):
            st.markdown(f"### {scheme['name']}")

            if reasons:
                st.success(
                    "Why you match the selected filters: "
                    + ", ".join(reasons)
                )
            else:
                st.info(
                    "Select profile chips to see match reasons."
                )

            st.write(scheme.get("eligibility_notes", ""))

            source = scheme.get("source_url", "")

            if source.startswith("https://"):
                st.link_button(
                    "Check official eligibility",
                    source,
                )

    if match_count == 0:
        st.info(
            "No schemes matched all selected filters. "
            "Try changing a profile chip."
        )

    st.caption(f"Showing {match_count} matching scheme cards.")
