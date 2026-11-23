"""Download and verify Chroma's ONNX model for container images."""

import hashlib
import tarfile
from pathlib import Path

import requests
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import (
    ONNXMiniLM_L6_V2,
)

REQUIRED_FILES = (
    "config.json",
    "model.onnx",
    "special_tokens_map.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "vocab.txt",
)


def model_is_cached(model_dir: Path) -> bool:
    return all((model_dir / filename).is_file() for filename in REQUIRED_FILES)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def safe_extract(archive: tarfile.TarFile, destination: Path) -> None:
    destination = destination.resolve()

    for member in archive.getmembers():
        target = (destination / member.name).resolve()

        if target != destination and destination not in target.parents:
            raise RuntimeError("Unsafe path in embedding model archive")

    archive.extractall(destination)


def cache_model() -> None:
    download_path = Path(ONNXMiniLM_L6_V2.DOWNLOAD_PATH)
    model_dir = download_path / ONNXMiniLM_L6_V2.EXTRACTED_FOLDER_NAME

    if model_is_cached(model_dir):
        print(f"Embedding model already cached at {model_dir}")
        return

    download_path.mkdir(parents=True, exist_ok=True)
    archive_path = download_path / ONNXMiniLM_L6_V2.ARCHIVE_FILENAME
    temp_path = archive_path.with_suffix(archive_path.suffix + ".tmp")

    try:
        with requests.get(
            ONNXMiniLM_L6_V2.MODEL_DOWNLOAD_URL,
            stream=True,
            timeout=(30, 300),
        ) as response:
            response.raise_for_status()

            with temp_path.open("wb") as file:
                for chunk in response.iter_content(1024 * 1024):
                    if chunk:
                        file.write(chunk)

        if sha256(temp_path) != ONNXMiniLM_L6_V2._MODEL_SHA256:
            raise RuntimeError("Embedding model checksum did not match")

        temp_path.replace(archive_path)

        with tarfile.open(archive_path, mode="r:gz") as archive:
            safe_extract(archive, download_path)

        if not model_is_cached(model_dir):
            raise RuntimeError("Embedding model archive was incomplete")

        archive_path.unlink()
        print(f"Cached embedding model at {model_dir}")

    finally:
        if temp_path.exists():
            temp_path.unlink()


if __name__ == "__main__":
    cache_model()
