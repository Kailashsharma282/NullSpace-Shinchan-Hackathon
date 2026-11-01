@echo off
echo ========================================================
echo   Starting NullSpace Epistemic Audit Platform
echo   See What the Sources Don't Say
echo ========================================================

cd /d "%~dp0"

echo [1/2] Initializing Python Virtual Environment...
if not exist "backend\.venv" (
    echo Creating virtual environment...
    python -m venv backend\.venv
    call backend\.venv\Scripts\pip install -r backend\requirements.txt
)

echo [2/2] Launching NullSpace Backend Server (Port 8080)...
start "NullSpace Backend Server" cmd /k "cd backend && .venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload"

echo [3/3] Opening browser...
timeout /t 3 >nul
start http://127.0.0.1:8080

echo NullSpace is running at http://127.0.0.1:8080
pause
