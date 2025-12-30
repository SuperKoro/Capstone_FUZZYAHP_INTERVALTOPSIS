@echo off
echo ========================================
echo   Rebuilding Supplier Selection
echo ========================================
echo.

REM Clean old build
echo [1/3] Cleaning old build...
if exist build rmdir /s /q build
if exist dist\SupplierSelection rmdir /s /q dist\SupplierSelection

echo [2/3] Building with PyInstaller...
echo This will take 3-5 minutes...
echo.

python -m PyInstaller main.py ^
    --onedir ^
    --windowed ^
    --name SupplierSelection ^
    --icon assets/icon.ico.ico ^
    --add-data "assets;assets" ^
    --add-data "resources;resources" ^
    --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Creating ZIP...
powershell -Command "Compress-Archive -Path 'dist\SupplierSelection\*' -DestinationPath 'dist\SupplierSelection_v1.0.1.zip' -Force"

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Executable: dist\SupplierSelection\SupplierSelection.exe
echo ZIP file: dist\SupplierSelection_v1.0.1.zip
echo.
echo Bug fixes included:
echo   - Fix expert rename crash
echo   - Fix TOPSIS weight validation warning
echo.
pause
