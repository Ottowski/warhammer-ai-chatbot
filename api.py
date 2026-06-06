import os
import sys
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure local imports work when running api.py directly.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.rag_pipeline import RAGPipeline


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent


def _writable_data_root() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "WH-AI-Chatbot"
    else:
        base = Path(__file__).resolve().parent
    base.mkdir(parents=True, exist_ok=True)
    return base


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    use_llm: bool = False


class AskResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]


rag_pipeline: RAGPipeline | None = None
_pipeline_ready: bool = False
_pipeline_status: str = "initializing"


def _init_pipeline_bg(pipeline: RAGPipeline) -> None:
    global _pipeline_ready, _pipeline_status
    try:
        pipeline.initialize_knowledge_base()
        _pipeline_ready = True
        _pipeline_status = "ready"
    except Exception as exc:
        _pipeline_status = f"error: {exc}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_pipeline

    resource_root = _resource_root()
    writable_root = _writable_data_root()

    rules_directory = resource_root / "rules"
    vector_store_path = writable_root / "data" / "vector_store"
    vector_store_path.mkdir(parents=True, exist_ok=True)

    rag_pipeline = RAGPipeline(
        rules_directory=str(rules_directory),
        vector_store_path=str(vector_store_path),
    )
    threading.Thread(target=_init_pipeline_bg, args=(rag_pipeline,), daemon=True).start()
    yield


app = FastAPI(
    title="Warhammer Rules Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/status")
def status() -> dict:
    return {"ready": _pipeline_ready, "message": _pipeline_status}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    if not _pipeline_ready:
        raise HTTPException(status_code=503, detail="Knowledge base is still loading, please wait a moment and try again.")

    try:
        result = rag_pipeline.answer_question(payload.question.strip(), use_llm=payload.use_llm)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}") from exc

    return AskResponse(
        query=result["query"],
        answer=result["answer"],
        sources=result.get("sources", []),
    )


frontend_dist = _resource_root() / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
