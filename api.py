import os
import re
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
        base = Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / "TOW-Arbiter"
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
# Cached at startup and returned to the frontend so it can make rule names clickable.
_special_rule_names: list[str] = []

# Load special rule names from the resource root at startup so they can be served to the frontend.
def _load_special_rule_names(resource_root: Path) -> list[str]:
    # Extract top-level special rule headings from the source markdown.
    special_rules_file = resource_root / "rules" / "special_rules.md"
    if not special_rules_file.exists():
        return []

    headings: list[str] = []
    ignored = {
        "What are Special Rules?",
        "Universal Special Rules",
        "Army Special Rules",
        "Unique Special Rules",
        "What Special Rules Does it Have?",
        "Rule Priority",
        "Cumulative Special Rules",
    }
    # Return the list of special rule headings extracted from the markdown file.
    for line in special_rules_file.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if not match:
            continue

        heading = match.group(1).strip()
        if heading and heading not in ignored:
            headings.append(heading)

    return headings

# Initialize the RAG pipeline in a background thread to avoid blocking the main application startup.
def _init_pipeline_bg(pipeline: RAGPipeline) -> None:
    global _pipeline_ready, _pipeline_status
    try:
        pipeline.initialize_knowledge_base()
        _pipeline_ready = True
        _pipeline_status = "ready"
    except Exception as exc:
        _pipeline_status = f"error: {exc}"

# Application lifespan context manager for initializing the RAG pipeline.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the RAG pipeline and load special rule names before the application starts serving requests.
    global rag_pipeline, _special_rule_names

    resource_root = _resource_root()
    writable_root = _writable_data_root()

    _special_rule_names = _load_special_rule_names(resource_root)

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
    title="TOW Arbiter API",
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


@app.get("/special-rules")
def special_rules() -> dict:
    # Frontend uses this list to convert rule names in answers into one-click follow-up searches.
    return {"special_rules": _special_rule_names}


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
