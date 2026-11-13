# GeoSentinel Enterprise GTOC - 1-Click Operations Launcher
# Enterprise Geopolitical Threat Intelligence & Asset Defense Suite

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "   GEOSENTINEL ENTERPRISE THREAT OPERATIONS CENTER (GTOC)" -ForegroundColor Yellow
Write-Host "   Global Intelligence & Supply Chain Geofencing Platform" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootDir

# 1. Verify Virtual Environment
$pythonExe = Join-Path $rootDir ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "[!] Virtual environment not detected at .venv. Checking standard python..." -ForegroundColor Yellow
    $pythonExe = "python"
}

# 2. Verify Frontend Dependencies
$frontendDir = Join-Path $rootDir "frontend"
$nodeModules = Join-Path $frontendDir "node_modules"
if (-not (Test-Path $nodeModules)) {
    Write-Host "[*] Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
    Push-Location $frontendDir
    npm install
    Pop-Location
}

# 3. Start Backend Uvicorn Process
Write-Host "[+] Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
$backendJob = Start-Process -FilePath $pythonExe -ArgumentList "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000" -WorkingDirectory $rootDir -PassThru

# Wait 2 seconds for backend socket
Start-Sleep -Seconds 2

# 4. Start Vite Frontend Process
Write-Host "[+] Launching Vite Frontend on http://localhost:5173 ..." -ForegroundColor Green
$frontendJob = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory $frontendDir -PassThru

# Wait 2 seconds for Vite bundler
Start-Sleep -Seconds 2

# 5. Open Default Browser to Dashboard
Write-Host "[+] Opening GeoSentinel AI in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host "   GEOSENTINEL ENTERPRISE GTOC COMMAND CENTER ONLINE" -ForegroundColor Green
Write-Host "   Backend API Docs : http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   Frontend Console : http://localhost:5173" -ForegroundColor White
Write-Host "   Active Geofences : Multi-tier corporate assets & chokepoints loaded" -ForegroundColor Cyan
Write-Host "   Press [ENTER] or close this window to terminate services." -ForegroundColor Yellow
Write-Host "========================================================`n" -ForegroundColor Green

try {
    [Console]::ReadLine()
} finally {
    Write-Host "[*] Shutting down GeoSentinel AI backend and frontend services..." -ForegroundColor Yellow
    if ($backendJob -and -not $backendJob.HasExited) {
        Stop-Process -Id $backendJob.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendJob -and -not $frontendJob.HasExited) {
        Stop-Process -Id $frontendJob.Id -Force -ErrorAction SilentlyContinue
    }
    # Clean up lingering node/uvicorn child processes if any
    Get-Process node, python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*$rootDir*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "[+] Services cleanly terminated. Ready for next run." -ForegroundColor Green
}
