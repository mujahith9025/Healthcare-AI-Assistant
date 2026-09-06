#!/usr/bin/env bash

echo "========================================================"
echo "   Starting AI Health Assistant & Clinical Intelligence"
echo "========================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 could not be found."
    echo "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

# Create Virtual Environment if not exists
if [ ! -d "venv" ]; then
    echo "[1/3] Creating Python Virtual Environment (venv)..."
    python3 -m venv venv
fi

# Activate Virtual Environment
source venv/bin/activate

# Install / Update Dependencies
echo "[2/3] Installing dependencies from requirements.txt..."
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[NOTICE] .env not found. Creating from .env.example..."
        cp .env.example .env
    fi
fi

# Launch Server
echo "[3/3] Launching local server at http://127.0.0.1:5000..."
echo ""
echo "========================================================"
echo "  Open your browser at: http://127.0.0.1:5000"
echo "  Press CTRL+C in this terminal to stop."
echo "========================================================"
echo ""

# Try opening default browser in background
if command -v open &> /dev/null; then
    open http://127.0.0.1:5000 &
elif command -v xdg-open &> /dev/null; then
    xdg-open http://127.0.0.1:5000 &
fi

# Run App
python3 app.py
