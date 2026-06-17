@echo off
chcp 65001 >nul
title Romih Agent v1.0 - Local

echo.
echo ========================================
echo    Romih Agent - Local Install
echo    Web UI + Telegram + 113 Tools
echo ========================================
echo.
echo Starting...
echo.

cd /d "%~dp0"
python run.py

echo.
echo Romih Agent stopped.
pause
