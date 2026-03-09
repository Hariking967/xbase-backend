@echo off
echo ========================================
echo XBase Python Backend Startup
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
echo     Python found!
echo.

echo [2/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo     Dependencies installed!
echo.

echo [3/3] Starting server...
echo     Server will run on http://localhost:8000
echo     Press Ctrl+C to stop
echo.
python main.py
