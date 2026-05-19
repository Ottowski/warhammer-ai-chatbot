# Warhammer Rules Assistant

An AI chatbot for Warhammer rules built with FastAPI + React.

## Desktop App (.exe)

Package the full app (backend + frontend + rules) as a native Windows desktop executable.

### Build

From the project root:

```powershell
.venv\Scripts\Activate.ps1
.\build_desktop.ps1
```

### Run

After the build finishes, start:

```powershell
dist\WH AI Chatbot.exe
```

Notes:
- The app opens in a native desktop window (pywebview).
- The frontend is bundled from `frontend/dist`.
- The backend API runs inside the app process.
- Persistent vector store data is written under `%LOCALAPPDATA%\WH-AI-Chatbot\data\vector_store` in desktop mode.

## Requirements

- Python 3.11 with a virtual environment (`.venv`)
- Node.js 18+
- Dependencies installed by the build script (`pip install -r requirements.txt` and `npm install`)
