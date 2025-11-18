@echo off
title Multi-Wizard Platform - Server Shutdown
echo ==================================================
echo Multi-Wizard Platform - Stopping Servers
echo ==================================================
echo.

REM Kill Node.js processes (Frontend)
echo [1/3] Stopping Frontend Server (Node.js)...
taskkill /F /IM node.exe /T 2>nul
if %errorlevel% equ 0 (
    echo       Frontend server stopped.
) else (
    echo       No frontend server running.
)

REM Kill Python processes (Backend)
echo [2/3] Stopping Backend Server (Python/Uvicorn)...
taskkill /F /FI "WINDOWTITLE eq Backend Server*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Frontend Server*" 2>nul

REM Alternative: Kill by process name if window title doesn't work
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| find "PID:"') do (
    wmic process where "ProcessId=%%a and CommandLine like '%%uvicorn%%'" call terminate >nul 2>&1
)

echo [3/3] Cleaning up...
timeout /t 2 /nobreak >nul

echo.
echo ==================================================
echo All Servers Stopped!
echo ==================================================
echo.
echo Press any key to exit...
pause >nul
