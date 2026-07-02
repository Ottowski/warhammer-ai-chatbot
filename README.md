# TOW Arbiter

An AI rules assistant for Warhammer: The Old World, built with FastAPI + React.

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
& ".\TOW Arbiter\TOW Arbiter.exe"
```

From another folder, use the full path:

```powershell
& "C:\Users\ottoa\OneDrive\Skrivbord\WH AI chatbot\TOW Arbiter\TOW Arbiter.exe"
```

Build and run in one go:

```powershell
Set-Location "C:\Users\ottoa\OneDrive\Skrivbord\WH AI chatbot"; .venv\Scripts\Activate.ps1; .\build_desktop.ps1; & ".\TOW Arbiter\TOW Arbiter.exe" 
```

Notes:
- The app opens in a native desktop window (pywebview).
- The frontend is bundled from `frontend/dist`.
- The backend API runs inside the app process.
- Persistent vector store data is written under `%LOCALAPPDATA%\TOW-Arbiter\data\vector_store` in desktop mode.
- In PowerShell, paths containing spaces must be quoted. Use `&` when launching executables.

## Requirements

- Python 3.11 with a virtual environment (`.venv`)
- Node.js 18+
- Dependencies installed by the build script (`pip install -r requirements.txt` and `npm install`)

---

## Mobile App (Android & iOS)

The mobile app is powered by a backend hosted on Render (free) and wrapped with Capacitor.

### Step 1 — Get a free Groq API key

1. Go to [console.groq.com](https://console.groq.com) and create a free account.
2. Generate an API key.

### Step 2 — Deploy the backend to Render

1. Push this repo to GitHub (if not already done).
2. Go to [render.com](https://render.com) → New → Web Service → connect your repo.
3. Render will detect `render.yaml` automatically. Click **Deploy**.
4. In the Render dashboard, go to **Environment** and add:
   - `GROQ_API_KEY` = your key from Step 1
5. After deploy, copy your service URL (e.g. `https://tow-arbiter-api.onrender.com`).

### Step 3 — Configure the mobile frontend

Edit `frontend/.env.mobile` and replace the placeholder with your Render URL:

```
VITE_API_URL=https://tow-arbiter-api.onrender.com
```

### Step 4 — Install Capacitor and add platforms

```powershell
cd frontend
npm install
npx cap add android   # Creates the Android project
# npx cap add ios     # macOS + Xcode only
```

### Step 5 — Build and sync

```powershell
npm run mobile:build   # Builds React with mobile env, copies to Capacitor
```

### Step 6 — Open in Android Studio / Xcode

```powershell
npx cap open android   # Opens Android Studio
# npx cap open ios     # Opens Xcode (macOS only)
```

Then build and run from Android Studio / Xcode onto a device or emulator.

> **Note:** After any frontend change, re-run `npm run mobile:build` then `npx cap open android` again.

