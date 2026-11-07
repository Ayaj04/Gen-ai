
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

BASE_URL = (
    "https://raw.githubusercontent.com/fastapi/fastapi/master/"
    "docs/en/docs/tutorial/"
)

PAGES = [
    "first-steps",
    "path-params",
    "query-params",
    "query-params-str-validations",
    "path-params-numeric-validations",
    "query-param-models",
    "body-multiple-params",
    "body-fields",
    "body-nested-models",
    "extra-data-types",
    "cookie-params",
    "header-params",
    "response-model",
    "response-status-code",
    "request-files",
    "handling-errors",
    "body",
    "schema-extra-example",
    "request-forms",
    "encoder",
]

# Keep the original tutorial landing page as an additional raw source.
LANDING_PAGE = "https://fastapi.tiangolo.com/tutorial/"


def download_document(filename: str, url: str) -> bool:
    output_path = RAW_DIR / filename
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        content = response.text
        if not content.strip():
            raise ValueError("Downloaded document is empty")

        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(output_path)

        print(f"Downloaded: {filename}")
        return True

    except (
        requests.exceptions.RequestException,
        OSError,
        ValueError,
    ) as error:
        print(f"Failed: {filename} - {error}")
        return False

    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass


def fetch_all():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    successful = 0

    # Individual tutorial pages are the primary dataset.
    for page in PAGES:
        filename = f"{page}.md"
        url = f"{BASE_URL}{filename}"

        if download_document(filename, url):
            successful += 1

    # Also retain the original tutorial landing page.
    if download_document("tutorial.html", LANDING_PAGE):
        successful += 1

    print(
        f"\nDownload complete: {successful} successful "
        f"out of {len(PAGES) + 1} attempted documents."
    )


if __name__ == "__main__":
    fetch_all()
