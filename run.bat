@echo off
title Smart AI Safety Guard - Localhost Launcher
echo ==============================================================================
echo           Smart AI Safety Guard - Automated Launch System
echo ==============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Verifying Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please install Python from https://www.python.org/
    echo Make sure to check the box: "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [2/3] Checking dependencies from requirements.txt...
python -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Package check encountered an issue. Retrying standard install...
    python -m pip install -r requirements.txt
)

echo [3/3] Launching Smart AI Safety Guard on Localhost...
echo.
echo ==============================================================================
echo  Opening your web browser at: http://localhost:8501
echo  Press Ctrl+C in this terminal window to stop the server when finished.
echo ==============================================================================
echo.

python -m streamlit run app.py --server.headless=false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Streamlit encountered an issue while running.
    pause
)
