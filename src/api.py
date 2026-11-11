from fastapi import FastAPI
from .__main__ import RAG
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="RAG API")
rag = RAG()




class SearchRequest(BaseModel):
    query: str
    method: Literal["bm25", "semantic", "hybrid"] = "bm25"
    k: int = 5


class AnswerRequest(BaseModel):
   query: str
   k: int


@app.post("/search")
def search(request: SearchRequest):
    query: request.query.strip()

    #if not query:
    #raise an error

    if request.method == "bm25":
        chunks, result = rag.search(query, request.k)

    elif request.method == "semantic":
        chunks, result = rag.semantic_search(query, request.k)

    elif request.hybrid == "hybrid":
        chunks = rag.hybrid_search(query, request.k)
        result = None

    return {
        "query": query,
        "method": request.method,
        "chunks": chunks,
        "search_result": (
            result.model_dump(mode="json") if result else None
        ),
    }


@app.post("/answer")
def answer(request: AnswerRequest):
    query = request.query.strip()
    
    #if not query:
    #raise error

    result = rag.answer(query, request.k)

    return result.model_dump(mode="json")



















