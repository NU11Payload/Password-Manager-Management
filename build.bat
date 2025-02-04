@echo off
echo Password Manager Analyzer Build System
echo ===================================
echo.
echo 1. Build Development Version (Standalone EXE)
echo 2. Build Installer
echo 3. Build Both
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    python build.py --dev-only
) else if "%choice%"=="2" (
    python build.py --installer-only
) else if "%choice%"=="3" (
    python build.py
) else (
    echo Invalid choice!
)

pause 