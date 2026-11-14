
from pathlib import Path
from urllib.parse import urlparse

from app.records import load_records
from app.ingest import clean_text


ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"


def split_text(text, chunk_size=120, overlap=25):
    """Split text into overlapping word chunks."""

    if not 0 <= overlap < chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    words = text.split()
    step = chunk_size - overlap
    chunks = []

    for start in range(0, len(words), step):
        part = words[start:start + chunk_size]

        if not part:
            break

        chunks.append(" ".join(part))

        if start + chunk_size >= len(words):
            break

    return chunks


def build_chunks():
    """Load raw documents and preserve source metadata."""

    all_chunks = []

    for record in load_records():
        source = record["source_url"]
        title = record["page_title"]

        # Match a record's source URL to its raw file
        filename = Path(urlparse(source).path).name

        if source.rstrip("/").endswith("/tutorial"):
            filename = "tutorial.html"

        raw_file = RAW_DIR / filename

        if not raw_file.is_file():
            print(f"Skipping missing file: {filename}")
            continue

        raw_text = raw_file.read_text(encoding="utf-8")
        text = clean_text(raw_text)
        page = raw_file.stem

        for index, part in enumerate(split_text(text)):
            all_chunks.append({
                "id": f"{page}-{index:04d}",
                "text": part,
                "title": title,
                "page": page,
                "source": source,
                "chunk_index": index,
            })

    return all_chunks


if __name__ == "__main__":
    chunks = build_chunks()

    print("Total chunks:", len(chunks))

    if chunks:
        print("First chunk:")
        print(chunks[0])
