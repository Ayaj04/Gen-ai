import subprocess
import sys


def test_api_startup_does_not_import_heavy_ai_dependencies():
    code = """
import sys

import app.main  # noqa: F401

heavy_modules = (
    "chromadb",
    "langgraph",
    "onnxruntime",
    "sentence_transformers",
    "sklearn",
    "torch",
)
loaded = [name for name in heavy_modules if name in sys.modules]

if loaded:
    raise SystemExit(f"Heavy modules loaded at startup: {loaded}")
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
