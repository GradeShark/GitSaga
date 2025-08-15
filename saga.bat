@echo off
REM GitSaga Batch Wrapper for Windows Command Prompt and PowerShell
REM This prevents console window flashing

set PYTHONIOENCODING=utf-8
chcp 65001 >nul 2>&1

python -m gitsaga.cli %*

if %ERRORLEVEL% NEQ 0 (
    python3 -m gitsaga.cli %*
)