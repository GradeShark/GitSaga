# GitSaga PowerShell Alias Installer
# This creates a permanent 'saga' command that doesn't flash

Write-Host "Installing GitSaga PowerShell alias..." -ForegroundColor Green

# Create the saga function
$sagaFunction = @'
function saga {
    $env:PYTHONIOENCODING = "utf-8"
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    python -m gitsaga.cli $args
}
'@

# Check if PowerShell profile exists
if (!(Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
    Write-Host "Created PowerShell profile at: $PROFILE" -ForegroundColor Yellow
}

# Check if saga function already exists
$profileContent = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
if ($profileContent -notlike "*function saga*") {
    # Add the function to profile
    Add-Content $PROFILE "`n# GitSaga Command (no console flashing)"
    Add-Content $PROFILE $sagaFunction
    Write-Host "✓ Added 'saga' command to PowerShell profile" -ForegroundColor Green
    Write-Host ""
    Write-Host "Please restart PowerShell or run:" -ForegroundColor Yellow
    Write-Host "  . `$PROFILE" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Then you can use 'saga' from anywhere without flashing!" -ForegroundColor Green
} else {
    Write-Host "saga command already exists in profile" -ForegroundColor Yellow
}

# Also create a batch file in Python Scripts folder for global access
$pythonScripts = Split-Path (Get-Command python).Source -Parent
$sagaBatPath = Join-Path $pythonScripts "saga-nf.bat"

$batContent = @"
@echo off
set PYTHONIOENCODING=utf-8
python -m gitsaga.cli %*
"@

Set-Content $sagaBatPath $batContent -Encoding ASCII
Write-Host "✓ Created saga-nf.bat (no-flash) in: $pythonScripts" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use either:" -ForegroundColor Cyan
Write-Host "  saga         (after restarting PowerShell)" -ForegroundColor White
Write-Host "  saga-nf      (works immediately, no flash)" -ForegroundColor White