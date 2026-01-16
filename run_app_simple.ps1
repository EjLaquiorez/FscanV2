# Simple script to run the Fruit Quality Scanner
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Fruit Quality Scanner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv_yolo")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup_project.ps1 first to set up the project." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run: .\setup_project.ps1" -ForegroundColor Cyan
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv_yolo\Scripts\Activate.ps1

# Check if Python is available
if (-not (Test-Path ".venv_yolo\Scripts\python.exe")) {
    Write-Host "ERROR: Python executable not found in virtual environment!" -ForegroundColor Red
    Write-Host "The virtual environment may be corrupted. Please run setup_project.ps1 again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host ""
Write-Host "The application will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run the app
& .\.venv_yolo\Scripts\python.exe app.py

