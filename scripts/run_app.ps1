# Run script for Fruit Quality Scanner
# Uses .venv_yolo virtual environment

Write-Host "Starting Fruit Quality Scanner..." -ForegroundColor Cyan
Write-Host ""

# Check if .venv_yolo exists
if (-not (Test-Path ".venv_yolo")) {
    Write-Host "ERROR: .venv_yolo virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first or install dependencies." -ForegroundColor Yellow
    exit 1
}

# Check for Python executable
$pythonPath = $null
if (Test-Path ".venv_yolo\Scripts\python.exe") {
    $pythonPath = ".venv_yolo\Scripts\python.exe"
} elseif (Test-Path ".venv_yolo\bin\python.exe") {
    $pythonPath = ".venv_yolo\bin\python.exe"
} else {
    Write-Host "ERROR: Python executable not found in .venv_yolo" -ForegroundColor Red
    exit 1
}

Write-Host "Using virtual environment: .venv_yolo" -ForegroundColor Green
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run the Flask app
& $pythonPath app.py

