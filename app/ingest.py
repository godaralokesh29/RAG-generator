import os
from dotenv import load_dotenv
from .rag import ingest_corpus


if __name__ == "__main__":
    load_dotenv()
    data_dir = os.getenv("DATA_DIR", "data")
    print(f"Ingesting documents from: {data_dir}")
    index, meta = ingest_corpus(data_dir)
    print(f"Indexed {len(meta)} chunks. Index saved.")
