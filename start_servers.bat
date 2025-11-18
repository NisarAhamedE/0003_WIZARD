@echo off
title Multi-Wizard Platform - Server Startup
echo ==================================================
echo Multi-Wizard Platform - Starting Servers
echo ==================================================
echo.

REM Start Backend Server
echo [1/2] Starting Backend Server (FastAPI)...
cd /d "%~dp0backend"
start "Backend Server - Port 8000" cmd /k "venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo [2/2] Starting Frontend Server (Vite)...
cd /d "%~dp0frontend"
start "Frontend Server - Port 3000" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ==================================================
echo Servers Started Successfully!
echo ==================================================
echo.
echo Backend API:    http://127.0.0.1:8000
echo API Docs:       http://127.0.0.1:8000/docs
echo Frontend App:   http://localhost:3000
echo.
echo Admin Login:    admin / Admin@123
echo.
echo Close this window or press any key to exit...
pause >nul
