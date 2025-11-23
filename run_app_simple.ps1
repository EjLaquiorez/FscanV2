# Simple script to run the Fruit Quality Scanner
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Fruit Quality Scanner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& .\.venv_yolo\Scripts\Activate.ps1

# Run the app
python app.py

