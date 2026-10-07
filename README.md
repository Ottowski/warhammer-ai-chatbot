# TOW Arbiter

An AI rules assistant for Warhammer: The Old World, built with FastAPI + React.

## Quick Start (fresh `git clone`)

Prerequisites: **Python 3.11** and **Node.js 18+** installed and on `PATH`.

Open PowerShell and run these commands (one-time build, takes several minutes):

```powershell
git clone https://github.com/Ottowski/warhammer-ai-chatbot.git
Set-Location warhammer-ai-chatbot
.\build_desktop.ps1
& ".\TOW Arbiter\TOW Arbiter.exe"
```

`build_desktop.ps1` does everything automatically: it creates `.venv`, installs the Python
and npm dependencies, builds the frontend, and packages the app. The script stops with an
error message if any step fails.

If PowerShell blocks the script, allow it for this session and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

After the first build, just launch the app (the build is not needed again unless the code changes):

```powershell
& ".\TOW Arbiter\TOW Arbiter.exe"
```

The first launch takes a while because the knowledge base is being indexed; the window shows a loading screen until it is ready.

## Run without building the .exe (development)

```powershell
Set-Location warhammer-ai-chatbot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

The API is then available at http://127.0.0.1:8000 (docs at `/docs`). To also serve the web UI, build the frontend first:

```powershell
npm --prefix frontend install
npm --prefix frontend run build
```

## Desktop App (.exe)

Package the full app (backend + frontend + rules) as a native Windows desktop executable.

### Build

From the project root (creates `.venv` automatically if it is missing):

```powershell
.\build_desktop.ps1
```

If your project path contains spaces, quote it:

```powershell
Set-Location "C:\path\to\warhammer-ai-chatbot"
.\build_desktop.ps1
```

### Run

```powershell
& ".\TOW Arbiter\TOW Arbiter.exe"
```

From another folder, use the full path:

```powershell
& "C:\path\to\warhammer-ai-chatbot\TOW Arbiter\TOW Arbiter.exe"
```

Build and run in one go:

```powershell
Set-Location "C:\path\to\warhammer-ai-chatbot"; .\build_desktop.ps1; & ".\TOW Arbiter\TOW Arbiter.exe"
```

Notes:
- The app opens in a native desktop window (pywebview).
- The frontend is bundled from `frontend/dist`.
- The backend API runs inside the app process.
- Persistent vector store data is written under `%LOCALAPPDATA%\TOW-Arbiter\data\vector_store` in desktop mode.
- In PowerShell, paths containing spaces must be quoted. Use `&` when launching executables.

## Requirements

- Python 3.11
- Node.js 18+
- Everything else (`.venv`, `pip install -r requirements.txt`, `npm install`) is handled by `build_desktop.ps1`

## Troubleshooting

- **`TOW Arbiter.exe` closes immediately:** the build was incomplete or stale. Re-run `.\build_desktop.ps1` and check it ends with `Build finished.`
- **Port 8000 already in use:** close any other running instance of the app or API server.
- **Running the script from another folder:** it switches to its own folder automatically.
