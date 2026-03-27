# Warhammer Rules Assistant

An AI chatbot for Warhammer rules built with FastAPI + React.

## Running the app

You need two terminals running at the same time.

### 1. Start the backend (API)

```bash
cd "WH AI chatbot"
.venv\Scripts\Activate.ps1
python -m uvicorn api:app --reload
```

Wait until you see `Application startup complete.` in the terminal (if you start the app the first time, it may take 10–30 seconds).

### 2. Start the frontend (React)

Open a new terminal:

```bash
cd "WH AI chatbot\frontend"
npm run dev
```

### 3. Open the browser

Navigate to: **http://localhost:5173**

---

## Requirements

- Python 3.10+ with a virtual environment (`.venv`)
- Node.js 18+
- Dependencies installed: `pip install -r requirements.txt` and `npm install`
- `uvicorn` is required for the backend and is already included in `requirements.txt`
