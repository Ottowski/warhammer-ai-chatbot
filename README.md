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

If your project path contains spaces, this also works from anywhere:

```powershell
Set-Location "C:\Users\ottoa\OneDrive\Skrivbord\WH AI chatbot"
.venv\Scripts\Activate.ps1
.\build_desktop.ps1
```

### Run

After the build finishes, start:

```powershell
& ".\dist\WH AI Chatbot.exe"
```

From another folder, use the full path:

```powershell
& "C:\Users\Input your user here\OneDrive\Desktop\WH AI chatbot\dist\WH AI Chatbot.exe"
```

Build and run in one go:

```powershell
Set-Location "C:\Users\Input your user here\OneDrive\Desktop\WH AI chatbot"; .venv\Scripts\Activate.ps1; .\build_desktop.ps1; & ".\dist\WH AI Chatbot.exe"
```

Notes:
- The app opens in a native desktop window (pywebview).
- The frontend is bundled from `frontend/dist`.
- The backend API runs inside the app process.
- Persistent vector store data is written under `%LOCALAPPDATA%\WH-AI-Chatbot\data\vector_store` in desktop mode.
- In PowerShell, paths containing spaces must be quoted. Use `&` when launching executables.

## Requirements

- Python 3.11 with a virtual environment (`.venv`)
- Node.js 18+
- Dependencies installed by the build script (`pip install -r requirements.txt` and `npm install`)
