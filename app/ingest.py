
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from app.models import Record


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"

BASE_URL = (
    "https://raw.githubusercontent.com/fastapi/fastapi/master/"
    "docs/en/docs/tutorial/"
)


class HTMLTextParser(HTMLParser):
    """Extract readable text and title from an HTML document."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.text_parts = []
        self.in_title = False
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag in {"script", "style", "noscript"}:
            self.skip_depth += 1
        elif tag == "title" and not self.skip_depth:
            self.in_title = True

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in {"script", "style", "noscript"} and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip_depth:
            return

        value = data.strip()
        if value:
            self.text_parts.append(value)
            if self.in_title:
                self.title_parts.append(value)


def strip_html(text: str) -> str:
    """Remove HTML tags while retaining their readable text."""
    parser = HTMLTextParser()
    parser.feed(text)
    parser.close()
    return " ".join(parser.text_parts)


def clean_text(text: str) -> str:
    """Remove common HTML and Markdown artifacts."""
    text = unescape(text)

    # Remove comments and MkDocs anchor attributes.
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(
        r"\{\s*#[\w-]+\s*\}",
        " ",
        text,
    )

    # Convert HTML tags to their text content.
    text = strip_html(text)

    # Remove Markdown images but retain link labels.
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove reference-style links, heading markers and formatting.
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    text = re.sub(r"(?m)^\s*[-*_]{3,}\s*$", " ", text)
    text = re.sub(r"[*_~]{1,3}", "", text)
    text = re.sub(r"`{1,3}", "", text)

    # Remove leftover HTML-like tags and collapse whitespace.
    text = re.sub(r"</?[A-Za-z][^>]*>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def read_document(path: Path) -> tuple[str, str]:
    raw = path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".html":
        parser = HTMLTextParser()
        parser.feed(raw)
        parser.close()

        title = " ".join(parser.title_parts).strip()
        text = " ".join(parser.text_parts)
    else:
        # Extract the title before cleaning Markdown syntax.
        match = re.search(r"(?m)^\s*#\s+(.+?)\s*$", raw)
        title = match.group(1).strip() if match else ""
        text = raw

    if not title:
        title = path.stem.replace("-", " ").title()

    return clean_text(title), text


def extract_section(text: str, title: str) -> str:
    headings = re.findall(
        r"(?m)^\s*#{1,6}\s+(.+?)\s*$",
        text,
    )

    for heading in headings:
        cleaned = clean_text(heading)
        if cleaned and cleaned.casefold() != title.casefold():
            return cleaned

    return title or "FastAPI Tutorial"


def extract_example(text: str) -> str:
    match = re.search(
        r"```[^\n]*\n(.*?)```",
        text,
        flags=re.DOTALL,
    )

    if not match:
        return ""

    # Code is intentionally preserved as code, not treated as prose.
    example = match.group(1).strip()
    return example[:1000]


def build_record(path: Path) -> Record:
    title, raw_text = read_document(path)

    if not raw_text.strip():
        raise ValueError("Document is empty")

    cleaned_text = clean_text(raw_text)

    if not cleaned_text:
        raise ValueError("No readable text after cleaning")

    section = extract_section(raw_text, title)

    symbol_match = re.search(
        r"\b(HTTPException|RequestValidationError|"
        r"FastAPI|BaseModel|APIRouter|Depends|"
        r"UploadFile|File|Form|Path|Query)\b",
        raw_text,
    )

    symbol = symbol_match.group(1) if symbol_match else "Not identified"

    if path.name == "tutorial.html":
        source_url = "https://fastapi.tiangolo.com/tutorial/"
    else:
        source_url = f"{BASE_URL}{path.name}"

    return Record(
        page_title=title,
        guide_section=section,
        key_concept=title,
        main_symbol=symbol,
        example_response=extract_example(raw_text),
        source_url=source_url,
    )


def ingest():
    records = []

    if not RAW_DIR.exists():
        print("Raw directory does not exist. Run app.fetch first.")
        return

    for path in sorted(RAW_DIR.iterdir()):
        if path.suffix.lower() not in {".md", ".html"}:
            continue

        try:
            record = build_record(path)
            records.append(record.to_dict())
            print(f"Processed: {path.name}")

        except (OSError, UnicodeError, ValueError, TypeError) as error:
            print(f"Skipping {path.name}: {error}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    print(f"\nSaved {len(records)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest()
