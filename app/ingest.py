
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from app.models import Record


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"

SOURCE_URLS = {
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


class HTMLTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts = []
        self.text_parts = []
        self.in_title = False
        self.ignored_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag in {"script", "style"}:
            self.ignored_depth += 1
        elif tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in {"script", "style"} and self.ignored_depth:
            self.ignored_depth -= 1
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.ignored_depth:
            return

        text = data.strip()
        if text:
            self.text_parts.append(text)
            if self.in_title:
                self.title_parts.append(text)


def read_document(path: Path):
    content = path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".html":
        parser = HTMLTextParser()
        parser.feed(content)
        parser.close()

        title = " ".join(parser.title_parts).strip()
        text = "\n".join(parser.text_parts)
    else:
        text = content
        match = re.search(r"(?m)^#\s+(.+)$", content)
        title = match.group(1).strip() if match else ""

    if not title:
        title = path.stem.replace("-", " ").title()

    return title, text


def build_record(path: Path) -> Record:
    title, text = read_document(path)

    if not text.strip():
        raise ValueError("Document is empty")

    headings = re.findall(r"(?m)^#{1,3}\s+(.+)$", text)
    section = headings[0].strip() if headings else "General Tutorial"

    symbols = re.findall(
        r"\b(?:HTTPException|RequestValidationError|"
        r"FastAPI|BaseModel|Path|Query)\b",
        text,
    )
    main_symbol = symbols[0] if symbols else "Not identified"

    example_match = re.search(
        r"```(?:json|python)?[ \t]*\n(.*?)```",
        text,
        re.DOTALL,
    )
    example = example_match.group(1).strip()[:1000] if example_match else ""

    return Record(
        page_title=title,
        guide_section=section,
        key_concept=main_symbol,
        main_symbol=main_symbol,
        example_response=example,
        source_url=SOURCE_URLS[path.name],
    )


def ingest():
    records = []

    if not RAW_DIR.exists():
        print("Raw data folder not found. Run app.fetch first.")
        return

    for path in sorted(RAW_DIR.iterdir()):
        if not path.is_file() or path.name not in SOURCE_URLS:
            continue

        try:
            record = build_record(path)
            records.append(record.to_dict())
            print(f"Processed: {path.name}")

        except (OSError, UnicodeError, ValueError, TypeError) as error:
            print(f"Skipping bad document {path.name}: {error}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    print(f"\nSaved {len(records)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest()
