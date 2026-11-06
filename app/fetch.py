
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

DOCUMENTS = {
    "tutorial.html": "https://fastapi.tiangolo.com/tutorial/",
    "handling-errors.md": (
        "https://raw.githubusercontent.com/fastapi/fastapi/master/"
        "docs/en/docs/tutorial/handling-errors.md"
    ),
    "first-steps.md": (
        "https://raw.githubusercontent.com/fastapi/fastapi/master/"
        "docs/en/docs/tutorial/first-steps.md"
    ),
}


def fetch_all():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    successful = 0

    for filename, url in DOCUMENTS.items():
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()

            output_path = RAW_DIR / filename
            output_path.write_text(
                response.text,
                encoding="utf-8",
            )

            print(f"Downloaded: {filename}")
            successful += 1

        except requests.exceptions.RequestException as error:
            print(f"Download failed for {filename}: {error}")

        except OSError as error:
            print(f"Could not save {filename}: {error}")

    print(f"\nSuccessfully downloaded {successful} of "
          f"{len(DOCUMENTS)} documents.")


if __name__ == "__main__":
    fetch_all()
