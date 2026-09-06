@echo off
title AI Health Assistant Launcher
echo ========================================================
echo    Starting AI Health Assistant & Clinical Intelligence
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please download and install Python from https://www.python.org/downloads/
    echo (Make sure to check 'Add Python to PATH' during installation!)
    echo.
    pause
    exit /b
)

:: Create Virtual Environment if it doesn't exist
if not exist "venv" (
    echo [1/3] Creating Python Virtual Environment (venv)...
    python -m venv venv
)

:: Activate Virtual Environment
call venv\Scripts\activate

:: Install / Update Dependencies
echo [2/3] Checking and installing dependencies from requirements.txt...
pip install -r requirements.txt --quiet

:: Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        echo [NOTICE] .env not found. Creating from .env.example...
        copy .env.example .env >nul
    )
)

:: Launch the Flask Application
echo [3/3] Launching local server at http://127.0.0.1:5000...
echo.
echo ========================================================
echo   Open your browser at: http://127.0.0.1:5000
echo   Press CTRL+C in this window to stop the application.
echo ========================================================
echo.

:: Open browser automatically after 2 seconds
start "" http://127.0.0.1:5000

:: Run the Flask App
python app.py

pause
