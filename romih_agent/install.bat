@echo off
chcp 65001 >nul
title Romih Agent - Setup

echo.
echo ========================================
echo    Romih Agent v1.0 - Installer
echo    141 tools - 6 enterprise plugins
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is required.
    echo Install from: https://python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install fastapi uvicorn httpx pydantic >nul 2>&1
echo       Done.

:: Check Telegram token
if "%TELEGRAM_BOT_TOKEN%"=="" (
    set TELEGRAM_BOT_TOKEN=8844618126:AAE-tPbM3__WNho1pTQp8SKEmaj5Gx--VxQ
)

:: Run Romih
echo [2/3] Starting Romih Agent...
echo.
echo ========================================
echo    Ready!
echo.
echo    Web UI:   http://localhost:8800/romih/
echo    Dashboard: http://localhost:8800/romih/dashboard
echo    Telegram: @RomihAgentbot
echo.
echo    Press Ctrl+C to stop
echo ========================================
echo.

cd /d "%~dp0"

:: Open browser after 3 seconds
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8800/romih/"

python run.py

echo.
echo Romih Agent stopped.
pause
