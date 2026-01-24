# Visual Project Overview

## File Tree

```
c:\Users\ottoa\OneDrive\Skrivbord\WH AI chatbot\
│
├─ 📄 SETUP_COMPLETE.md          ← You are here
├─ 📄 QUICKSTART.md              ← Start here!
├─ 📄 README.md                  ← Full documentation
├─ 📄 ARCHITECTURE.md            ← Technical details
│
├─ 🚀 MAIN APPLICATION
│  ├─ main.py                    ← RUN THIS: python main.py
│  ├─ verify_setup.py            ← Check setup: python verify_setup.py
│  └─ config.ini                 ← Configuration template
│
├─ 📦 DEPENDENCIES
│  └─ requirements.txt           ← pip install -r requirements.txt
│
├─ 🐍 SOURCE CODE
│  └─ src/
│     ├─ __init__.py
│     ├─ rag_pipeline.py         ← Main orchestrator
│     ├─ vector_store.py         ← Chroma database
│     ├─ embeddings.py           ← Sentence-transformers
│     └─ document_loader.py      ← Load & chunk rules
│
├─ 📖 RULE DOCUMENTS (ADD YOUR OWN!)
│  └─ rules/
│     ├─ core_rules.md           ← Movement, combat, morale
│     ├─ army_building.md        ← Army composition
│     └─ game_phases.md          ← Turn structure
│
├─ 💾 DATA (AUTO-CREATED)
│  └─ data/
│     └─ vector_store/           ← Chroma embeddings (created on first run)
│
├─ 🚀 LLM INTEGRATION EXAMPLES
│  ├─ examples_with_llm.py       ← OpenAI ChatGPT
│  └─ examples_with_ollama.py    ← Local Ollama LLM
│
└─ 🔧 CONFIGURATION
   └─ .gitignore                 ← Git configuration
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (You!)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Types question
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                      main.py (CLI)                            │
│  - Accepts input                                              │
│  - Formats output                                             │
│  - Shows sources                                              │
└────────────┬────────────────────────────────────────────────┘
             │
             │ Calls
             ↓
┌──────────────────────────────────────────────────────────────┐
│              src/rag_pipeline.py (Orchestrator)              │
│  - Coordinates all components                                 │
│  - Manages workflow                                           │
│  - Returns formatted results                                  │
└──┬───────────┬─────────────┬──────────────────────┬──────────┘
   │           │             │                      │
   │ Initialize│             │                      │
   ↓           │             │                      │
┌──────┐       │             │                      │
│rules │       │             │                      │
│  *.md│       │             │                      │
└──┬───┘       │             │                      │
   │           │             │                      │
   │ Loads ↓   │ Uses    ↓   │ Queries ↓        ↓ Generates
   │           │             │
┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐
│  DocumentLoader │  │  Embeddings      │  │ VectorStore  │
│  (doc_loader)   │  │  (embeddings)    │  │ (vector_store)
│                 │  │                  │  │              │
│ - Reads files   │  │ - sentence-      │  │ - Chroma DB  │
│ - Chunks text   │  │   transformers   │  │ - Persisted  │
│ - Metadata      │  │ - all-MiniLM-    │  │ - Similarity │
│                 │  │   L6-v2          │  │   search     │
└─────────────────┘  └──────────────────┘  └──────────────┘
```

## Data Flow - Query Example

```
USER INPUT: "How do I move a unit?"
                    ↓
    ┌───────────────────────────────┐
    │  Convert to embeddings        │
    │  (numerical vector)           │
    └────────────┬──────────────────┘
                 ↓
    ┌───────────────────────────────┐
    │  Search vector store          │
    │  (semantic similarity)        │
    └────────────┬──────────────────┘
                 ↓
    ┌───────────────────────────────┐
    │  Top-3 Matches Found:         │
    │  1. core_rules.md: Movement   │
    │  2. game_phases.md: Movement  │
    │  3. core_rules.md: Charges    │
    └────────────┬──────────────────┘
                 ↓
    ┌───────────────────────────────┐
    │  Format answer + sources      │
    └────────────┬──────────────────┘
                 ↓
         DISPLAY TO USER:
    ┌───────────────────────────────┐
    │ Answer: [Relevant rules...]   │
    │                               │
    │ Sources:                      │
    │ 1. core_rules.md              │
    │ 2. game_phases.md             │
    └───────────────────────────────┘
```

## Workflow: First Run vs Subsequent Runs

### First Run (Setup)
```
python main.py
    ↓
[FIRST RUN INITIALIZATION]
    ├─ Download embedding model (50MB) → ~30 seconds
    ├─ Read rules/ directory
    ├─ Chunk documents
    ├─ Generate embeddings
    ├─ Store in Chroma
    └─ Save to data/vector_store/
    ↓
Ready for questions!
```

### Subsequent Runs (Fast)
```
python main.py
    ↓
[SUBSEQUENT RUNS]
    ├─ Load cached embedding model → ~1 second
    ├─ Load Chroma from disk
    ├─ Ready for questions → Instant
    ↓
Waiting for input...
```

## Integration Paths

```
                      CURRENT SETUP
                    (main.py - CLI)
                           ↓
                  ┌─────────────────┐
                  │  RAG Pipeline   │
                  │  (src/*.py)     │
                  └────────┬────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ↓               ↓               ↓
    ┌────────────┐  ┌─────────────┐  ┌──────────┐
    │  GUI       │  │  Web API    │  │   LLM    │
    │(Tkinter)   │  │(FastAPI)    │  │(OpenAI/  │
    │            │  │             │  │ Ollama)  │
    │ examples:  │  │ examples:   │  │ examples:│
    │ See        │  │ See ARCH    │  │ with_llm │
    │ ARCH       │  │.md          │  │.py       │
    └────────────┘  └─────────────┘  └──────────┘
```

## When to Use Each Module

| Module | When to Use | Key Method |
|--------|-----------|-----------|
| `main.py` | Running the app | `main()` |
| `rag_pipeline.py` | Question answering | `answer_question()` |
| `vector_store.py` | Searching embeddings | `query()` |
| `embeddings.py` | Converting text→vectors | `get_embedding_function()` |
| `document_loader.py` | Loading new rules | `load_all_documents()` |

## Speed Comparison

```
Operation              Time         Why?
─────────────────────────────────────────────────
First run              30-60 sec    Download embedding model
Load on 2nd run        <1 sec       Use cached model
Single query           50-200 ms    Vector similarity search
Query + LLM answer     1-5 sec      Call OpenAI/Ollama API
Add 100 documents      5-10 sec     Generate embeddings
```

## Memory Usage

```
Component           Memory Used    Notes
────────────────────────────────────────────
Embedding model     100-200 MB     Varies by model size
Vector store        50-100 MB      Grows with documents
LLM (local)         4-8 GB         For Ollama
LLM (API)           0 MB           Remote service
Idle app            30-50 MB       Just Python + libraries
```

## Example Questions & Expected Results

```
Q: "How do I move a unit?"
A: [Retrieved from core_rules.md + game_phases.md]
   Shows movement mechanics, modifiers
   Sources: core_rules.md, game_phases.md
   Time: ~100ms

Q: "What are character restrictions?"
A: [Retrieved from army_building.md]
   Shows 25% character limit rule
   Sources: army_building.md
   Time: ~100ms

Q: "Explain morale checks"
A: [Retrieved from core_rules.md + game_phases.md]
   Shows morale mechanics, thresholds
   Sources: core_rules.md, game_phases.md
   Time: ~120ms
```

## Customization Flowchart

```
Want to extend?
     │
     ├─→ Add GUI?           See ARCHITECTURE.md
     │
     ├─→ Add API?           See ARCHITECTURE.md
     │
     ├─→ Use ChatGPT?       Run examples_with_llm.py
     │
     ├─→ Use Local LLM?     Run examples_with_ollama.py
     │
     ├─→ More rules?        Add .md/.txt to rules/
     │
     ├─→ Different model?   Edit src/embeddings.py
     │
     └─→ Docker deploy?     See ARCHITECTURE.md
```

## File Sizes

```
File                          Size    Purpose
──────────────────────────────────────────────
main.py                      3 KB    CLI interface
src/rag_pipeline.py          5 KB    Orchestrator
src/vector_store.py          4 KB    Vector database
src/embeddings.py            2 KB    Embeddings wrapper
src/document_loader.py       5 KB    Document loading
rules/*.md                   ~30 KB  Sample rules (your docs)
data/vector_store/*          ~5 MB   Embeddings (auto-created)
```

---

## Ready? Let's Go! 🚀

```bash
# Step 1: Install
pip install -r requirements.txt

# Step 2: Verify (optional)
python verify_setup.py

# Step 3: Run!
python main.py

# Step 4: Ask questions
Your question: How do I move a unit?
```

**Next:** Read [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.
