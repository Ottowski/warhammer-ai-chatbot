$ErrorActionPreference = 'Stop'

$iconPngPath = 'frontend/public/iconikai-icon-pack/web/android-chrome-512x512.png'
$iconIcoPath = 'frontend/public/app_icon.ico'

if (Test-Path $iconPngPath) {
  Write-Host 'Generating Windows ICO from icon pack...'
  & .\.venv\Scripts\python.exe -c "
from PIL import Image
src = '$iconPngPath'.replace('\\\\','/')
dst = '$iconIcoPath'.replace('\\\\','/')
img = Image.open(src).convert('RGBA')
img.save(dst, format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('ICO saved to', dst)
"
}
else {
  Write-Warning "Icon source not found at $iconPngPath. Building without custom EXE icon."
}

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
  --onedir `
  --windowed `
  --name "WH AI Chatbot" `
  --icon "frontend/public/app_icon.ico" `
  --add-data "rules;rules" `
  --add-data "frontend/dist;frontend/dist" `
  --collect-all webview `
  app_launcher.py

Write-Host ''
Write-Host 'Build finished.'
Write-Host 'Executable: dist\WH AI Chatbot\WH AI Chatbot.exe'
