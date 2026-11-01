#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  Starting NullSpace Epistemic Audit Platform"
echo "  See What the Sources Don't Say"
echo "========================================================"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -d "backend/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv backend/.venv
    backend/.venv/bin/pip install -r backend/requirements.txt
fi

echo "Launching NullSpace Backend Server..."
export PYTHONPATH=backend
backend/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

echo "NullSpace is running at http://localhost:8000"
echo "Press Ctrl+C to stop."
wait $SERVER_PID

