import os
from typing import List, Tuple
from pypdf import PdfReader


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_md(path: str) -> str:
    return read_txt(path)


def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n".join(texts)


def load_documents(data_dir: str) -> List[Tuple[str, str]]:
    """Return list of (source_path, text). Supports .pdf, .txt, .md"""
    docs = []
    for root, _, files in os.walk(data_dir):
        for name in files:
            path = os.path.join(root, name)
            low = name.lower()
            if low.endswith(".pdf"):
                text = read_pdf(path)
            elif low.endswith(".txt"):
                text = read_txt(path)
            elif low.endswith(".md"):
                text = read_md(path)
            else:
                continue

            text = (text or "").strip()
            if text:
                docs.append((path, text))
    return docs


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    text = text.replace("\r", "")
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)

        if end == n:
            break

        start = max(0, end - overlap)

    return chunks
