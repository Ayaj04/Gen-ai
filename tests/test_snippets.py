import ast
from pathlib import Path

from streamlit.testing.v1 import AppTest

from ui.snippets import cited_snippets, load_snippets


def test_official_examples_have_valid_python_and_attribution():
    snippets = load_snippets()
    assert len(snippets) == 20
    assert len({item["page"] for item in snippets}) == len(snippets)
    for item in snippets:
        ast.parse(item["code"])
        assert item["source"].startswith("docs_src/")
        assert item["source_url"].endswith(item["source"])
        assert item["revision"] in item["source_url"]
        assert item["docs_url"].startswith("https://fastapi.tiangolo.com/tutorial/")


def test_citations_match_raw_and_public_docs_urls():
    snippets = load_snippets()
    for source in [
        "https://fastapi.tiangolo.com/tutorial/handling-errors/",
        "https://raw.githubusercontent.com/fastapi/fastapi/master/docs/en/docs/tutorial/handling-errors.md",
    ]:
        result = cited_snippets([{"source": source}], snippets)
        assert [item["page"] for item in result] == ["handling-errors"]
    assert cited_snippets([], snippets) == []
    assert cited_snippets([{"page": "not-bundled"}], snippets) == []


def test_snippet_card_renders_cited_code_and_empty_state():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "ui" / "app.py").run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ["💬 Documentation chat", "Snippet card"]
    app.session_state.messages = [{
        "id": "test-answer", "role": "assistant", "content": "Use HTTPException [1].",
        "citations": [{"page": "handling-errors", "title": "Handling Errors",
                       "source": "https://fastapi.tiangolo.com/tutorial/handling-errors/"}],
    }]
    app.run()
    app.radio[1].set_value("Latest cited docs").run()
    assert not app.exception
    assert "raise HTTPException" in app.code[0].value
    app.session_state.messages = []
    app.run()
    app.radio[1].set_value("Latest cited docs").run()
    assert not app.code
    assert any("No bundled Python example" in item.value for item in app.info)


def test_missing_catalog_shows_recovery_message(monkeypatch):
    def missing_catalog():
        raise FileNotFoundError("Catalog missing")

    monkeypatch.setattr("ui.snippets.load_snippets", missing_catalog)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "ui" / "app.py").run()
    assert not app.exception
    assert any("restore data/snippets.json" in item.value for item in app.error)
