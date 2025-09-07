import os
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .rag import answer_query, search

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(title="RAG Backend (Gemini + FAISS)")

# ----- CORS Setup (for MERN/frontend) -----
origins = [
    os.getenv("CORS_ORIGIN", "*"),
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Models -----
class AskBody(BaseModel):
    query: str
    top_k: Optional[int] = None


# ----- Endpoints -----
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/search")
async def search_get(query: str, top_k: Optional[int] = None):
    res = search(query, top_k or int(os.getenv("TOP_K", 5)))
    return {"results": res}


@app.post("/ask")
async def ask(body: AskBody):
    res = answer_query(body.query, top_k=body.top_k)
    return res
