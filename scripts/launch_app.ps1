# GeoSentinel AI Application Launcher
$ErrorActionPreference = "Continue"
$rootDir = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $rootDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   LAUNCHING GEOSENTINEL AI PLATFORM" -ForegroundColor Yellow
Write-Host "   Global Geopolitical Threat Intelligence & Defense" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$pythonExe = Join-Path $rootDir ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

# 1. Start Backend FastAPI
Write-Host "[+] Starting FastAPI backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath $pythonExe -ArgumentList "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000" -WorkingDirectory $rootDir -PassThru
Write-Host "    Backend started with Process ID: $($backendProcess.Id)" -ForegroundColor DarkCyan

# Allow backend 3 seconds to initialize schema and spin up socket
Start-Sleep -Seconds 3

# 2. Start Frontend Vite
$frontendDir = Join-Path $rootDir "frontend"
Write-Host "[+] Starting Vite frontend on http://localhost:5173 ..." -ForegroundColor Green
$frontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory $frontendDir -PassThru
Write-Host "    Frontend started with Process ID: $($frontendProcess.Id)" -ForegroundColor DarkCyan

# Allow Vite 3 seconds to spin up dev server
Start-Sleep -Seconds 3

# 3. Health Probe Backend
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 5
    Write-Host "[OK] Backend Operational: Status = $($health.status), Platform = $($health.project)" -ForegroundColor Green
} catch {
    Write-Host "[!] Backend initializing, please allow a few seconds..." -ForegroundColor Yellow
}

# 4. Open Default Web Browser
Write-Host "[+] Launching Dashboard in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "   APPLICATION IS LIVE AND READY IN YOUR BROWSER" -ForegroundColor Green
Write-Host "   Frontend Dashboard : http://localhost:5173" -ForegroundColor White
Write-Host "   Backend API Docs   : http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   WebSocket Live Feed: ws://127.0.0.1:8000/ws/alerts" -ForegroundColor White
Write-Host "========================================================`n" -ForegroundColor Green

