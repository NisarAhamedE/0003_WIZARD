@echo off
title Multi-Wizard Platform - Server Restart
echo ==================================================
echo Multi-Wizard Platform - Restarting Servers
echo ==================================================
echo.

REM Stop servers first
call "%~dp0stop_servers.bat"

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start servers
call "%~dp0start_servers.bat"
