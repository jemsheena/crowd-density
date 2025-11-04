# PowerShell script to install dependencies with proper numpy handling
# This script installs numpy first to let pip find the best version for Python 3.13

Write-Host "Installing numpy first (to find Python 3.13 compatible version)..." -ForegroundColor Yellow
pip install --upgrade pip
pip install numpy

Write-Host "Installing remaining dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "Installation complete!" -ForegroundColor Green

