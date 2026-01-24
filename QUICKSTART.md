# Quick Start Guide - WH AI Chatbot

## Step 1: Prerequisites

Ensure you have **Python 3.11 or higher** installed:

```bash
python --version
```

## Step 2: Install Dependencies

In your terminal/PowerShell, navigate to the project folder and run:

```bash
pip install -r requirements.txt
```

This will install:
- **chromadb**: Vector database for storing embeddings
- **sentence-transformers**: For embedding documents
- **langchain**: Framework for building LLM applications
- **openai**: Optional, for ChatGPT integration

**First run note**: The embedding model (~50MB) will download automatically on first run.

## Step 3: Add Rule Documents

The application looks for rule files in the `rules/` directory.

Sample files are included:
- `rules/core_rules.md` - Movement, combat, morale
- `rules/army_building.md` - Army composition
- `rules/game_phases.md` - Turn structure

**To add more rules**:
1. Create `.md` or `.txt` files in `rules/` folder
2. The app auto-loads all files on startup
3. Use clear headings (# for sections, ## for subsections)

## Step 4: Run the Application

```bash
python main.py
```

You should see:
```
============================================================
WARHAMMER: THE OLD WORLD - AI RULES ASSISTANT
============================================================
Ask questions about the rules in natural language
Type 'exit' or 'quit' to quit

Loading knowledge base...
Initialized embeddings with model: all-MiniLM-L6-v2
Loaded existing collection: warhammer_rules
Added 15 document chunks to collection
Vector store persisted to disk
✓ Ready to answer questions!

Your question: 
```

## Step 5: Ask Questions

Examples:

```
Your question: How do I move a unit?
Your question: What are armor saves?
Your question: When do I need to take a morale check?
Your question: Can I charge through difficult terrain?
```

The app will:
1. Search the knowledge base for relevant rules
2. Show the most relevant excerpts
3. Cite the source documents

## Troubleshooting

### "No rule files found"
- Ensure `.md` or `.txt` files are in `rules/` directory
- Check file encoding is UTF-8 (not ANSI)
- Verify file names have correct extensions

### "ModuleNotFoundError: No module named 'chromadb'"
```bash
pip install chromadb sentence-transformers
```

### Application runs slowly on first execution
This is normal! The embedding model downloads (~50MB) on first run. Subsequent runs use the cached model and are much faster.

### How to clear the vector store and rebuild
```bash
# Delete the vector store folder
rmdir /s data\vector_store

# OR on Mac/Linux:
rm -rf data/vector_store

# Then run the app again
python main.py
```

## Next Steps: Add LLM Integration

The basic app shows you the raw rule text. To add AI-generated answers:

### Option A: Use ChatGPT (Easy, requires API key)
```bash
pip install openai langchain-openai
python examples_with_llm.py
```

[Set OPENAI_API_KEY environment variable first](https://platform.openai.com/account/api-keys)

### Option B: Use Local LLM - Ollama (Free, no API key)
```bash
# 1. Download Ollama from https://ollama.ai
# 2. Run: ollama pull llama2
# 3. Install: pip install ollama
# 4. Run: python examples_with_ollama.py
```

## File Structure Explanation

```
WH-AI-Chatbot/
│
├── main.py                    # Entry point - run this!
├── requirements.txt           # Dependencies to install
├── README.md                  # Full documentation
│
├── src/
│   ├── rag_pipeline.py       # Orchestrates retrieval + generation
│   ├── vector_store.py       # Manages Chroma database
│   ├── embeddings.py         # Embedding model (sentence-transformers)
│   └── document_loader.py    # Loads and chunks rule files
│
├── rules/                    # Your rule documents go here
│   ├── core_rules.md
│   ├── army_building.md
│   └── game_phases.md
│
└── data/
    └── vector_store/         # Auto-created - don't edit
```

## Understanding the RAG Architecture

**RAG = Retrieval Augmented Generation**

1. **Retrieval**: Your question is converted to embeddings and compared against stored rule embeddings to find the most relevant sections
2. **Context**: The top 3 most relevant rule excerpts are retrieved
3. **Generation**: 
   - Basic mode: Shows you the raw excerpts and sources
   - With LLM: Feeds excerpts to an AI model for a natural answer

```
User Question
    ↓
Embedding (all-MiniLM-L6-v2)
    ↓
Vector Search (Chroma)
    ↓
Top 3 Results + Sources
    ↓
Display to User [OR]
    ↓
Send to LLM (GPT/Ollama)
    ↓
Natural Language Answer
```

## Customization Tips

### Use Different Embedding Model
Edit `src/embeddings.py`:
```python
# Faster but less accurate
model_name = "all-MiniLM-L6-v2"  # ← Default

# Slower but better quality
model_name = "all-mpnet-base-v2"
```

### Change Number of Results
Edit `src/rag_pipeline.py` in `answer_question()`:
```python
relevant_docs, metadatas = self.retrieve_context(query, top_k=5)  # Default is 3
```

### Adjust Chunk Sizes
Edit `src/document_loader.py`:
```python
chunk_size = 500  # Smaller = more precise, larger = more context
```

## Advanced: Building a GUI or API

Once this works, you can extend it:

### Add Tkinter GUI
```python
from tkinter import Tk, Label, Entry, Text

root = Tk()
question = Entry(root)
answer_display = Text(root)
```

### Add FastAPI Backend
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/ask")
async def ask(query: str):
    return rag.answer_question(query)
```

The core RAG pipeline is already structured to support these easily!

## Support

For issues:
1. Check that Python 3.11+ is installed
2. Verify all dependencies: `pip list`
3. Ensure rules/ directory has .md or .txt files
4. Check that rules are properly formatted (UTF-8 encoding)

Happy querying!
