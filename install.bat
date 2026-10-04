@echo off
chcp 65001 >nul
title Article Generator - Install
cd /d "%~dp0"

echo ============================================================
echo    Article Generator  -  install
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [Error] Python not found in PATH.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/
    echo Make sure to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [1/2] Creating virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [Error] Failed to create the virtual environment.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [1/2] Virtual environment .venv already exists
)

echo [2/2] Installing dependencies (fastapi, uvicorn, ollama, httpx) ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo [Error] Failed to install dependencies.
    echo Check your internet connection and run this script again.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo    Installation complete.
echo    Start the app with:  start.bat
echo ============================================================
echo.
pause
exit /b 0
