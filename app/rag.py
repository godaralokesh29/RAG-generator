import os
import pickle
from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import google.generativeai as genai

from .utils import load_documents, chunk_text

# Load environment variables
load_dotenv()

# ----- Config -----
INDEX_DIR = os.getenv("INDEX_DIR", "storage")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 120))
TOP_K = int(os.getenv("TOP_K", 5))
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-1.5-flash")
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", 14000))

# Ensure storage directory exists
os.makedirs(INDEX_DIR, exist_ok=True)
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
META_PATH = os.path.join(INDEX_DIR, "meta.pkl")

# ----- Embeddings -----
_embedder = None


def get_embedder():
    """Lazily load the embedding model (singleton)."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def embed_texts(texts: List[str]) -> np.ndarray:
    """Return float32 numpy array of embeddings for a list of texts."""
    emb = get_embedder().encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.array(emb).astype("float32")


# ----- Index persistence -----
def save_index(index: faiss.IndexFlatIP, meta: List[Dict]):
    """Save FAISS index + metadata."""
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(meta, f)


def load_index() -> Tuple[faiss.IndexFlatIP, List[Dict]]:
    """Load FAISS index + metadata if available."""
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
        raise FileNotFoundError("Index not found. Run ingestion first.")
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)
    return index, meta


# ----- Ingestion -----
def ingest_corpus(data_dir: str = "data") -> Tuple[faiss.IndexFlatIP, List[Dict]]:
    """Ingest all documents under `data_dir` into FAISS index."""
    docs = load_documents(data_dir)
    records = []  # each: {"source": str, "chunk": str}

    for src, text in docs:
        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for c in chunks:
            records.append({"source": src, "chunk": c})

    if not records:
        raise ValueError("No documents found to ingest.")

    texts = [r["chunk"] for r in records]
    mat = embed_texts(texts)  # shape (N, D)

    index = faiss.IndexFlatIP(mat.shape[1])  # cosine via normalized embeddings
    index.add(mat)

    save_index(index, records)
    return index, records
