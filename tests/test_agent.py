
from app.agent_loop import choose_tool
from app.tools import http_status_explainer


def test_http_status_404():
    result = http_status_explainer(404)

    assert result["code"] == "404"
    assert result["name"] == "Not Found"
    assert result["fix_hint"]


def test_http_status_422():
    result = http_status_explainer(422)

    assert result["code"] == "422"
    assert result["meaning"]


def test_unknown_http_status():
    result = http_status_explainer(999)

    assert "error" in result


def test_agent_selects_http_tool():
    tool, code = choose_tool(
        "What does HTTP 404 mean?"
    )

    assert tool == "http_status_explainer"
    assert code == "404"


def test_agent_selects_rag():
    tool, code = choose_tool(
        "How do I use path parameters?"
    )

    assert tool == "rag"
    assert code is None
