@echo off
setlocal EnableDelayedExpansion
title AI Health Assistant Launcher

echo ========================================================
echo    Starting AI Health Assistant - Clinical Intelligence
echo ========================================================
echo.

:: Detect Python command (python or py launcher)
set PY_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
) else (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PY_CMD=py
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python is not installed or not in your Windows PATH.
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check the box: Add Python to PATH during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected: %PY_CMD%
echo.

:: Create Virtual Environment if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Setting up Python Virtual Environment...
    %PY_CMD% -m venv venv
)

:: Activate Virtual Environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

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

:: Open browser automatically
start "" http://127.0.0.1:5000

:: Run the Flask App
python app.py

pause
