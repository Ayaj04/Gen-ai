
import csv
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = ROOT / "data" / "http_status_codes.csv"


@lru_cache(maxsize=1)
def load_status_codes():
    """Load the CSV once into a dictionary."""

    status_codes = {}

    with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            status_codes[row["code"]] = row

    return status_codes


def http_status_explainer(code):
    """Look up one HTTP status code without any API."""

    code = str(code).strip()
    status_codes = load_status_codes()

    return status_codes.get(
        code,
        {
            "code": code,
            "error": "Status code not found in local CSV",
        },
    )


if __name__ == "__main__":
    print(http_status_explainer(404))
