@echo off
echo ========================================
echo Restarting Backend Server
echo ========================================

echo.
echo Step 1: Stopping existing backend servers...
taskkill /F /PID 12012 2>nul
taskkill /F /PID 25680 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting backend server...
cd backend
start "Backend Server" cmd /k "venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"

echo.
echo ========================================
echo Backend server restarting...
echo Wait 5 seconds for server to initialize
echo ========================================
timeout /t 5 /nobreak

echo.
echo Backend server should now be running on http://localhost:8000
echo Check the new window for any errors
echo.
pause
