@echo off
chcp 65001 >nul
title Romih Agent - Setup

echo.
echo ========================================
echo    Romih Agent v1.0 - Installer
echo    AI Agent - 141 tools
echo ========================================
echo.

:: Step 1: Check Python
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo Python not found. Installing...
    echo Downloading Python 3.12...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
    echo Installing Python (this may take a few minutes)...
    "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1
    del "%TEMP%\python_installer.exe"
    echo Python installed.
    :: Refresh PATH
    call :refresh_env
)

echo    Python OK.

:: Step 2: Install dependencies
echo [2/4] Installing packages...
pip install fastapi uvicorn httpx pydantic --quiet
echo    Done.

:: Step 3: Create desktop shortcut
echo [3/4] Creating shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "TARGET=%~dp0run.bat"
set "ICON=%~dp0romih.ico"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\Romih Agent.lnk'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'Romih Agent - AI Agent'; $s.Save()"
echo    Shortcut created on Desktop.

:: Step 4: Set Telegram token (user can override)
if "%TELEGRAM_BOT_TOKEN%"=="" (
    set "TELEGRAM_BOT_TOKEN=8844618126:AAE-tPbM3__WNho1pTQp8SKEmaj5Gx--VxQ"
)

:: Ready
echo [4/4] Starting Romih Agent...
echo.
echo ========================================
echo.
echo    Romih Agent is starting...
echo.
echo    Web:     http://localhost:8800/romih/
echo    Telegram: @RomihAgentbot
echo.
echo    Press Ctrl+C to stop
echo    Double-click "Romih Agent" on Desktop
echo.
echo ========================================
echo.

cd /d "%~dp0"

:: Open browser
start /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8800/romih/"

:: Run
python run.py

echo.
echo Romih Agent stopped. Goodbye!
pause
exit /b 0

:refresh_env
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH') do set "SYSTEMPATH=%%b"
set "PATH=%PATH%;%SYSTEMPATH%"
exit /b 0
