# Architecture & Extension Guide

## Project Architecture

### RAG (Retrieval Augmented Generation) Pipeline

The application uses a three-stage RAG architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUESTION                             │
│                  "How do I move a unit?"                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │  EMBEDDING & RETRIEVAL             │
    │  Convert question to embeddings    │
    │  Search vector store for matches   │
    │  Return top-3 relevant documents   │
    └────────────┬─────────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────────┐
    │  CONTEXT PREPARATION               │
    │  Format retrieved documents        │
    │  Cite sources                      │
    │  Prepare for generation            │
    └────────────┬─────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
         ↓                ↓
    ┌─────────────┐  ┌──────────────────┐
    │ OUTPUT MODE │  │ LLM MODE         │
    │ Display raw │  │ (Optional)       │
    │ excerpts    │  │ Send to ChatGPT  │
    │             │  │ or Ollama        │
    └─────────────┘  └──────────────────┘
         │                │
         └───────┬────────┘
                 ↓
         ┌────────────────────┐
         │   FINAL ANSWER     │
         │   + SOURCES        │
         └────────────────────┘
```

## Module Breakdown

### 1. `main.py` - Application Entry Point
- **Purpose**: User interface and main control flow
- **Responsibilities**:
  - Accept user questions
  - Call RAG pipeline
  - Format and display results
- **Extensible for**: CLI → GUI → Web API

### 2. `src/embeddings.py` - Embedding Management
- **Purpose**: Convert text to numerical vectors
- **Model**: sentence-transformers (all-MiniLM-L6-v2)
- **Key Method**: `get_embedding_function()`
- **Can be replaced with**:
  - OpenAI embeddings
  - HuggingFace alternatives
  - Custom trained embeddings

### 3. `src/vector_store.py` - Vector Database
- **Purpose**: Store and search embeddings
- **Backend**: Chroma (with DuckDB persistence)
- **Key Methods**:
  - `add_documents()` - Index new documents
  - `query()` - Semantic search
  - `persist()` - Save to disk
- **Alternatives**:
  - FAISS (Facebook AI Similarity Search)
  - Pinecone (cloud)
  - Weaviate (open source)

### 4. `src/document_loader.py` - Rule Processing
- **Purpose**: Load and chunk rule documents
- **Features**:
  - Recursive directory scanning
  - Intelligent text chunking with overlap
  - Metadata preservation (file source)
- **Customization Points**:
  - Chunk size
  - Overlap strategy
  - File type support

### 5. `src/rag_pipeline.py` - Orchestration
- **Purpose**: Coordinates all components
- **Main Method**: `answer_question()`
- **Flow**:
  1. Initialize all components
  2. Load documents
  3. Retrieve relevant context
  4. Generate answer
  5. Return with citations

## Data Flow

```
SETUP PHASE:
Rules Files → Document Loader → Chunked Documents
                                       ↓
Chunked Docs → Embeddings → Vector Store (Persisted to Disk)

QUERY PHASE:
User Question → Embeddings → Vector Search
                                 ↓
Top-3 Matches → Format Answer → Display to User
                     ↓
              (Optional) LLM Generation
```

## Extensibility Points

### 1. Adding GUI (Tkinter/PyQt)

Replace the CLI interface in `main.py`:

```python
# main.py
from tkinter import Tk, Button, Text, Entry

class WhChatbotGUI:
    def __init__(self):
        self.root = Tk()
        self.rag = RAGPipeline()
        self.setup_ui()
    
    def setup_ui(self):
        # Add widgets
        self.question_input = Entry(self.root)
        self.answer_display = Text(self.root)
        Button(self.root, text="Ask", command=self.on_ask).pack()
    
    def on_ask(self):
        query = self.question_input.get()
        result = self.rag.answer_question(query)
        self.answer_display.insert("1.0", result["answer"])
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = WhChatbotGUI()
    gui.run()
```

### 2. Adding FastAPI Backend

Create a new file `api.py`:

```python
from fastapi import FastAPI
from src.rag_pipeline import RAGPipeline

app = FastAPI()
rag = RAGPipeline()
rag.initialize_knowledge_base()

@app.post("/ask")
async def ask_question(question: str):
    """Endpoint for asking questions"""
    result = rag.answer_question(question)
    return result

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
```

Run with: `uvicorn api:app --reload`

### 3. Integrating LLM (OpenAI)

Modify `src/rag_pipeline.py`:

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

class RAGPipeline:
    def __init__(self, ...):
        # ... existing code ...
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
    
    def generate_answer(self, query: str, context: str) -> str:
        """Generate using LLM"""
        prompt = PromptTemplate(
            template="Answer based on: {context}\n\nQ: {query}\nA:",
            input_variables=["context", "query"]
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(context=context, query=query)
```

### 4. Using Alternative Vector Store (FAISS)

Replace in `src/vector_store.py`:

```python
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class VectorStoreManager:
    def __init__(self):
        embeddings = HuggingFaceEmbeddings()
        self.vector_store = FAISS.from_documents(
            documents=docs,
            embedding=embeddings
        )
    
    def query(self, question: str):
        return self.vector_store.similarity_search(question, k=3)
```

### 5. Adding Search Filters

Enhance `vector_store.py`:

```python
def query_with_filters(self, query: str, filters: dict, top_k: int = 3):
    """Query with metadata filtering"""
    # Only search within specific source files
    if "source" in filters:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"source": {"$eq": filters["source"]}}
        )
    return results
```

### 6. Adding Custom Chunking Strategy

Replace in `src/document_loader.py`:

```python
def _chunk_by_sections(self, text: str) -> List[str]:
    """Smart chunking by markdown headers"""
    chunks = []
    current_chunk = ""
    
    for line in text.split("\n"):
        if line.startswith("#"):
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += "\n" + line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks
```

## Performance Optimization

### 1. Embedding Model Selection
```python
# Fast (recommended for local)
"all-MiniLM-L6-v2"  # 22MB, ~5ms/query

# Better quality
"all-mpnet-base-v2"  # 430MB, ~100ms/query

# For GPU
"all-MiniLM-L6-v2-cuda"
```

### 2. Batch Processing
```python
# In document_loader.py
for batch in self._batch_documents(documents, batch_size=32):
    embeddings = self.embedding_manager.embed_texts(batch)
    # Process...
```

### 3. Caching
```python
# In rag_pipeline.py
from functools import lru_cache

@lru_cache(maxsize=100)
def retrieve_context_cached(self, query: str):
    return self.vector_store.query(query)
```

## Testing Structure (Optional)

Create `tests/test_rag_pipeline.py`:

```python
import pytest
from src.rag_pipeline import RAGPipeline

def test_initialization():
    rag = RAGPipeline()
    assert rag is not None

def test_retrieve_context():
    rag = RAGPipeline()
    rag.initialize_knowledge_base()
    docs, meta = rag.retrieve_context("movement")
    assert len(docs) > 0

def test_answer_question():
    rag = RAGPipeline()
    rag.initialize_knowledge_base()
    result = rag.answer_question("How do I move?")
    assert "answer" in result
```

Run with: `pytest tests/`

## Deployment Options

### 1. Command Line (Current)
```bash
python main.py
```

### 2. Web API
```bash
pip install fastapi uvicorn
python api.py
# Visit http://localhost:8000/docs
```

### 3. Docker Container
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### 4. Executable (PyInstaller)
```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

## Best Practices

1. **Always cite sources** - Users need to know where answers come from
2. **Keep chunks sized appropriately** - Too small loses context, too large is imprecise
3. **Validate rule documents** - Ensure consistent formatting for better chunking
4. **Version control embeddings** - Note which embedding model was used
5. **Monitor performance** - Track query times and relevance scores
6. **Test with new rules** - Verify retrieval quality when adding documents

## Future Enhancements

- [ ] Multi-language support
- [ ] Conversation memory (remember previous questions)
- [ ] Rule version management
- [ ] User feedback loop (rate answer quality)
- [ ] Advanced filtering by rule category
- [ ] Streaming responses for LLM answers
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
