$ErrorActionPreference = 'Stop'

Write-Host 'Building frontend...'
Push-Location frontend
npm install
npm run build
Pop-Location

Write-Host 'Installing Python dependencies...'
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host 'Creating desktop executable with PyInstaller...'
& .\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name "WH AI Chatbot" `
  --add-data "rules;rules" `
  --add-data "frontend/dist;frontend/dist" `
  --collect-all webview `
  app_launcher.py

Write-Host ''
Write-Host 'Build finished.'
Write-Host 'Executable: dist\WH AI Chatbot.exe'
