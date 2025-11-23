@echo off
echo ========================================
echo Starting Fruit Quality Scanner
echo ========================================
echo.

REM Activate virtual environment
call .venv_yolo\Scripts\activate.bat

REM Run the app
python app.py

pause

