import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure local imports work when running api.py directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import RAGPipeline


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    use_llm: bool = False


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]


rag_pipeline: RAGPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_pipeline
    rag_pipeline = RAGPipeline(
        rules_directory="./rules",
        vector_store_path="./data/vector_store",
    )
    rag_pipeline.initialize_knowledge_base()
    yield


app = FastAPI(
    title="Warhammer Rules Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="Knowledge base is not initialized yet")

    try:
        result = rag_pipeline.answer_question(payload.question.strip(), use_llm=payload.use_llm)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}") from exc

    return AskResponse(
        query=result["query"],
        answer=result["answer"],
        sources=result.get("sources", []),
    )
