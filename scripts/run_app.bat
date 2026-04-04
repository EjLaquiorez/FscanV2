@echo off
REM Run script for Fruit Quality Scanner
REM Uses .venv_yolo virtual environment

echo Starting Fruit Quality Scanner...
echo.

REM Prefer .venv then .venv_yolo
set PYTHON_PATH=
if exist ".venv\Scripts\python.exe" (
    set PYTHON_PATH=.venv\Scripts\python.exe
    set VENV_NAME=.venv
) else if exist ".venv_yolo\Scripts\python.exe" (
    set PYTHON_PATH=.venv_yolo\Scripts\python.exe
    set VENV_NAME=.venv_yolo
)
if "%PYTHON_PATH%"=="" (
    echo ERROR: No .venv or .venv_yolo found. Run: python -m venv .venv
    echo Then: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Using virtual environment: %VENV_NAME%
echo Starting Flask application...
echo.
echo The application will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
%PYTHON_PATH% app.py

pause

