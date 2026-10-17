@echo off
:: ─────────────────────────────────────────
:: JARVIS Launcher
:: Starts JARVIS silently in background
:: ─────────────────────────────────────────

cd /d "%~dp0"

:: Check if Python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

:: Start JARVIS (hidden window)
start /min "" pythonw main.py

echo JARVIS is starting...
timeout /t 2 /nobreak >nul
