@echo off
echo ========================================
echo Clearing Cache for Fresh Start
echo ========================================
echo.

REM Stop running Python processes
taskkill /F /IM python.exe 2>nul
echo Stopped Python processes

REM Clear Python cache
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo Cleared Python __pycache__ folders

REM Clear .pyc files
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
echo Cleared .pyc files

REM Clear Flask session
if exist .flask_session rd /s /q .flask_session 2>nul
echo Cleared Flask session cache

REM Clear uploaded images
if exist static\images\uploads\*.jpg del /q static\images\uploads\*.jpg 2>nul
if exist static\images\uploads\*.png del /q static\images\uploads\*.png 2>nul
if exist static\images\uploads\*.jpeg del /q static\images\uploads\*.jpeg 2>nul

REM Clear processed images
if exist static\images\processed\*.jpg del /q static\images\processed\*.jpg 2>nul
if exist static\images\processed\*.png del /q static\images\processed\*.png 2>nul
if exist static\images\processed\*.jpeg del /q static\images\processed\*.jpeg 2>nul
echo Cleared uploaded/processed images

echo.
echo ========================================
echo Cache Cleanup Complete!
echo ========================================
echo.
echo Ready for a fresh start!
echo.
pause

