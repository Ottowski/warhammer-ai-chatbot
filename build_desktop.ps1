$ErrorActionPreference = 'Stop'

$iconPngPath = 'frontend/public/iconikai-icon-pack/web/android-chrome-512x512.png'
$iconIcoPath = 'frontend/public/app_icon.ico'

Set-Location $PSScriptRoot

if (-not (Test-Path '.\.venv\Scripts\python.exe')) {
  Write-Host 'Creating Python virtual environment (.venv)...'
  python -m venv .venv
  if ($LASTEXITCODE -ne 0) {
    throw 'Failed to create .venv. Install Python 3.11 and make sure "python" is on PATH.'
  }
}

Write-Host 'Installing Python dependencies...'
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
  throw 'Failed to install Python dependencies.'
}

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
if ($LASTEXITCODE -ne 0) {
  throw 'Failed to generate the application icon.'
}
}
else {
  Write-Warning "Icon source not found at $iconPngPath. Building without custom EXE icon."
}

Write-Host 'Building frontend...'
Push-Location frontend
npm install
if ($LASTEXITCODE -ne 0) {
  throw 'Failed to install frontend dependencies.'
}
npm run build
if ($LASTEXITCODE -ne 0) {
  throw 'Failed to build the frontend.'
}
Pop-Location

Write-Host 'Creating desktop executable with PyInstaller...'
& .\.venv\Scripts\python.exe -m PyInstaller `
  --noconfirm `
  --clean `
  --onedir `
  --windowed `
  --distpath "." `
  --name "TOW Arbiter" `
  --icon "frontend/public/app_icon.ico" `
  --add-data "rules;rules" `
  --add-data "frontend/dist;frontend/dist" `
  --collect-all webview `
  app_launcher.py
if ($LASTEXITCODE -ne 0) {
  throw 'Failed to create the desktop executable.'
}

Write-Host ''
Write-Host 'Build finished.'
Write-Host 'Executable: TOW Arbiter\TOW Arbiter.exe'
