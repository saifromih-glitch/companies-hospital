@echo off
chcp 65001 >nul
title Romih Agent - Local Runner

echo.
echo ╔══════════════════════════════════════════╗
echo ║          Romih Agent - Local Runner       ║
echo ║          v1.0 - 74 tools active           ║
echo ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"
python run_local.py

echo.
echo Romih Agent exited.
pause
