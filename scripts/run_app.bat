@echo off
REM Run script for Fruit Quality Scanner
REM Uses .venv_yolo virtual environment

echo Starting Fruit Quality Scanner...
echo.

REM Check if .venv_yolo exists
if not exist ".venv_yolo" (
    echo ERROR: .venv_yolo virtual environment not found!
    echo Please create it first or install dependencies.
    pause
    exit /b 1
)

REM Check for Python executable
set PYTHON_PATH=
if exist ".venv_yolo\Scripts\python.exe" (
    set PYTHON_PATH=.venv_yolo\Scripts\python.exe
) else if exist ".venv_yolo\bin\python.exe" (
    set PYTHON_PATH=.venv_yolo\bin\python.exe
) else (
    echo ERROR: Python executable not found in .venv_yolo
    pause
    exit /b 1
)

echo Using virtual environment: .venv_yolo
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

