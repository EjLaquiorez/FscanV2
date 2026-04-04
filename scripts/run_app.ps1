# Run script for Fruit Quality Scanner
# Uses .venv_yolo virtual environment

Write-Host "Starting Fruit Quality Scanner..." -ForegroundColor Cyan
Write-Host ""

# Prefer .venv, then .venv_yolo, then system python on PATH
$pythonPath = $null
$venvName = $null
if (Test-Path ".venv\Scripts\python.exe") {
    $pythonPath = ".venv\Scripts\python.exe"
    $venvName = ".venv"
} elseif (Test-Path ".venv_yolo\Scripts\python.exe") {
    $pythonPath = ".venv_yolo\Scripts\python.exe"
    $venvName = ".venv_yolo"
} elseif (Test-Path ".venv\bin\python.exe") {
    $pythonPath = ".venv\bin\python.exe"
    $venvName = ".venv"
} elseif (Test-Path ".venv_yolo\bin\python.exe") {
    $pythonPath = ".venv_yolo\bin\python.exe"
    $venvName = ".venv_yolo"
}

if (-not $pythonPath) {
    Write-Host "ERROR: No virtual environment found. Create one and install requirements:" -ForegroundColor Red
    Write-Host '  python -m venv .venv' -ForegroundColor Yellow
    Write-Host '  .\.venv\Scripts\Activate.ps1' -ForegroundColor Yellow
    Write-Host '  pip install -r requirements.txt' -ForegroundColor Yellow
    exit 1
}

Write-Host "Using virtual environment: $venvName" -ForegroundColor Green
Write-Host "Starting Flask application..." -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will be available at:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Run the Flask app
& $pythonPath app.py

