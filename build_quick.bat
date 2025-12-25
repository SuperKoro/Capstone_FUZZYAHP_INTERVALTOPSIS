@echo off
REM ========================================
REM Quick Build Script (Batch Version)
REM Supplier Selection Application
REM ========================================

echo ========================================
echo   Building Supplier Selection v1.0.0
echo ========================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo [1/2] Building executable...
echo This may take 5-10 minutes...
echo.

REM Build with PyInstaller
python -m PyInstaller --onedir --windowed --name SupplierSelection --icon assets/icon.ico.ico main.py --hidden-import PyQt6 --hidden-import sqlite3 --hidden-import numpy --add-data "assets;assets" --add-data "resources;resources" --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed!
echo.

echo [2/2] Checking output...
if exist "dist\SupplierSelection\SupplierSelection.exe" (
    echo [SUCCESS] Executable found: dist\SupplierSelection\SupplierSelection.exe
) else (
    echo [ERROR] Executable not found!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Executable location:
echo   dist\SupplierSelection\SupplierSelection.exe
echo.
echo To create installer, run:
echo   iscc SupplierSelection_Setup.iss
echo.

pause
