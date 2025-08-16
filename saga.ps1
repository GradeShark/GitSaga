# SagaShark PowerShell Wrapper
# This script ensures proper execution in PowerShell without console flashing

$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Find Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Error "Python not found. Please install Python 3.8 or later."
    exit 1
}

# Run SagaShark
& $python.Source -m sagashark.cli $args