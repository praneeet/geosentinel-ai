@echo off
title GeoSentinel Enterprise GTOC - Mission Launcher
color 0b

echo ========================================================
echo    GEOSENTINEL ENTERPRISE THREAT OPERATIONS CENTER (GTOC)
echo    Real-Time Geopolitical Risk, Asset Defense & Playbooks
echo ========================================================
echo.

cd /d "%~dp0"

echo [+] Launching Enterprise Suite via PowerShell runner...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_demo.ps1"

pause
