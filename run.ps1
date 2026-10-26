Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "          Smart AI Safety Guard - VS Code PowerShell Launcher" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# 1. Check Python
try {
    $pyVer = python --version
    Write-Host "[1/3] Python verified: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ (Check 'Add to PATH')"
    exit 1
}

# 2. Check dependencies
Write-Host "[2/3] Checking requirements..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet

# 3. Launch Streamlit
Write-Host "[3/3] Starting website on localhost:8501..." -ForegroundColor Green
Write-Host "Opening http://localhost:8501 in your browser..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server when done." -ForegroundColor Gray
Write-Host ""

python -m streamlit run app.py
