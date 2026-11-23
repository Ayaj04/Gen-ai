"""A small explicit injection guard, not a complete security classifier."""

import re

INJECTION = re.compile(
    r"\b(?:ignore|disregard|override|forget)\b.{0,80}\b(?:instructions|system prompt|rules)\b"
    r"|\b(?:reveal|print|show|leak)\b.{0,80}\b(?:system prompt|api[_ ]?key|secrets?)\b",
    re.IGNORECASE | re.DOTALL,
)


def is_prompt_injection(text):
    return bool(INJECTION.search(text))


def validate_question(text):
    if is_prompt_injection(text):
        raise ValueError("Instruction overrides and requests for secrets are not supported")
    return text
