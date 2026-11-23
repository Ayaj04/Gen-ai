"""Offline tutorial examples with pinned, official source attribution."""

import json
from pathlib import Path
from urllib.parse import urlparse

SNIPPETS_FILE = Path(__file__).resolve().parents[1] / "data" / "snippets.json"


def load_snippets():
    return json.loads(SNIPPETS_FILE.read_text(encoding="utf-8"))


def cited_snippets(citations, snippets):
    """Match only bundled topics actually cited by the latest answer."""
    pages = set()
    for citation in citations:
        page = citation.get("page", "")
        if page:
            pages.add(page)
        source = citation.get("source", "")
        pages.add(Path(urlparse(source).path.rstrip("/")).stem)
    return [snippet for snippet in snippets if snippet["page"] in pages]
