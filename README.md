# Warhammer: The Old World - AI Chatbot

A local Python application using RAG (Retrieval Augmented Generation) to answer questions about Warhammer: The Old World rules.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Rule Documents
Place your rule documents (`.md` or `.txt` files) in the `rules/` directory. Sample rules are included.

### 3. Run the Application
```bash
python main.py
```

The application will:
- Load rules from the `rules/` directory
- Build a vector store (first run takes ~30 seconds to download embeddings)
- Accept questions interactively
- Return relevant rules and source citations

### Example Questions
- "How do I move a unit?"
- "What are armor saves?"
- "How do morale checks work?"
- "What is a charge?"
- "How many units can I have as characters?"

## Project Structure

```
WH-AI-Chatbot/
├── main.py                      # Main application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── src/                         # Core application modules
│   ├── __init__.py
│   ├── rag_pipeline.py          # Main RAG orchestration
│   ├── vector_store.py          # Chroma vector store management
│   ├── embeddings.py            # Sentence-transformers embeddings
│   └── document_loader.py       # Rule document loading & chunking
│
├── rules/                       # Rule documents (markdown/text)
│   ├── core_rules.md
│   ├── army_building.md
│   └── game_phases.md
│
└── data/
    └── vector_store/            # Persisted vector store (auto-created)
```

## Architecture

### RAG Pipeline
1. **Retrieval**: Embeds user question and searches vector store for relevant rule sections
2. **Context**: Returns top 3 most relevant documents with source information
3. **Generation**: Presents extracted rules and sources (ready for LLM integration)

### Components
- **EmbeddingManager**: Uses sentence-transformers (`all-MiniLM-L6-v2`) for efficient embeddings
- **VectorStoreManager**: Manages Chroma database with persistence
- **DocumentLoader**: Loads markdown/text files and chunks them intelligently
- **RAGPipeline**: Orchestrates the entire retrieval and generation process

## Future Enhancements

### Desktop GUI
```python
# Future: Use Tkinter or PyQt6 for GUI
from PyQt6.QtWidgets import QApplication, QMainWindow
```

### FastAPI Backend
```python
# Future: REST API for web/mobile clients
from fastapi import FastAPI

@app.post("/ask")
async def ask_question(question: str):
    return rag.answer_question(question)
```

### LLM Integration
Choose one approach:

**A. Local LLM via Ollama (Recommended)**
```bash
# Install ollama from https://ollama.ai
# Run: ollama pull llama2
```

**B. OpenAI API**
```python
from langchain.chat_models import ChatOpenAI
import os
os.environ["OPENAI_API_KEY"] = "your-key"
```

**C. Other Models**
- HuggingFace Transformers
- Claude API
- Cohere API

## Configuration

### Embedding Model Options
Edit `src/embeddings.py` to change the embedding model:

```python
# Fast, low memory (recommended for local)
model_name = "all-MiniLM-L6-v2"

# Slower, better quality
model_name = "all-mpnet-base-v2"

# Multilingual support
model_name = "distiluse-base-multilingual-cased-v2"
```

### Vector Store Settings
Edit `src/vector_store.py` to customize storage location or behavior.

## Troubleshooting

### "No module named 'chromadb'"
```bash
pip install chromadb sentence-transformers
```

### "No rule files found"
- Ensure `.md` or `.txt` files are in the `rules/` directory
- Check file permissions and encoding (UTF-8 recommended)

### Slow on first run
- First run downloads the embedding model (~50MB)
- Subsequent runs use cached model
- Building vector store takes ~30 seconds

### Memory issues
- Use a smaller embedding model: `all-MiniLM-L6-v2` (fastest)
- Reduce chunk sizes in `document_loader.py`
- Limit documents to most essential rules

## Development Notes

### Adding Custom Rule Files
1. Create a `.md` or `.txt` file in `rules/` directory
2. Run the application - it auto-loads new files
3. Vector store is automatically rebuilt if needed

### Extending with LLM
The `RAGPipeline.generate_answer()` method is where you'd integrate:

```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

def generate_answer(self, query: str, context: str):
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt = PromptTemplate(template="...", input_variables=["query", "context"])
    return llm(prompt.format(query=query, context=context))
```

### Custom Chunking
Modify the `_chunk_text()` method in `document_loader.py` for different chunking strategies:
- Smaller chunks: More precise retrieval, more documents
- Larger chunks: Less precise, faster

## Performance Tips

- Use `all-MiniLM-L6-v2` for fast local inference
- Keep rule documents in `.md` format for easier parsing
- Test with a small rules set first before adding comprehensive rules
- Consider using GPU acceleration if available (Chroma and sentence-transformers support CUDA)

## License

Warhammer: The Old World is a trademark of Games Workshop Limited.
This project is for personal/educational use only.
