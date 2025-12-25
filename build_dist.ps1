# ========================================
# Build Distribution Script
# Supplier Selection Application
# ========================================

param(
    [switch]$SkipInstaller,
    [switch]$Clean
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Building Supplier Selection v1.0.0  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set error action
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# ========================================
# Step 1: Clean old builds (optional)
# ========================================
if ($Clean) {
    Write-Host "[1/4] Cleaning old builds..." -ForegroundColor Yellow
    
    if (Test-Path "build") {
        Remove-Item -Path "build" -Recurse -Force
        Write-Host "  ✓ Removed build/" -ForegroundColor Green
    }
    
    if (Test-Path "dist") {
        Remove-Item -Path "dist" -Recurse -Force
        Write-Host "  ✓ Removed dist/" -ForegroundColor Green
    }
    
    if (Test-Path "*.spec") {
        Remove-Item -Path "*.spec" -Force
        Write-Host "  ✓ Removed .spec file" -ForegroundColor Green
    }
    
    Write-Host ""
}

# ========================================
# Step 2: Check dependencies
# ========================================
Write-Host "[2/4] Checking dependencies..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    exit 1
}

# Check PyInstaller
try {
    $pyinstallerVersion = python -m PyInstaller --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ PyInstaller: $pyinstallerVersion" -ForegroundColor Green
    } else {
        throw "PyInstaller not installed"
    }
} catch {
    Write-Host "  ✗ PyInstaller not found. Installing..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Failed to install PyInstaller!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ PyInstaller installed" -ForegroundColor Green
}

Write-Host ""

# ========================================
# Step 3: Build executable with PyInstaller
# ========================================
Write-Host "[3/4] Building executable..." -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Gray

$buildStartTime = Get-Date

# Build command
$buildArgs = @(
    "-m", "PyInstaller",
    "--onedir",
    "--windowed",
    "--name", "SupplierSelection",
    "--icon", "assets/icon.ico.ico",
    "main.py",
    "--hidden-import", "PyQt6",
    "--hidden-import", "sqlite3",
    "--hidden-import", "numpy",
    "--add-data", "assets;assets",
    "--add-data", "resources;resources",
    "--noconfirm"
)

# Run PyInstaller
python @buildArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Build failed!" -ForegroundColor Red
    exit 1
}

$buildEndTime = Get-Date
$buildDuration = ($buildEndTime - $buildStartTime).TotalSeconds

Write-Host "  ✓ Build completed in $([math]::Round($buildDuration, 1))s" -ForegroundColor Green

# Check if executable exists
if (Test-Path "dist\SupplierSelection\SupplierSelection.exe") {
    $exeSize = (Get-Item "dist\SupplierSelection\SupplierSelection.exe").Length / 1MB
    Write-Host "  ✓ Executable: SupplierSelection.exe ($([math]::Round($exeSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Executable not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ========================================
# Step 4: Create installer (optional)
# ========================================
if (-not $SkipInstaller) {
    Write-Host "[4/4] Creating installer..." -ForegroundColor Yellow
    
    # Check if Inno Setup is installed
    $isccPaths = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        "C:\Program Files\Inno Setup 5\ISCC.exe"
    )
    
    $isccPath = $null
    foreach ($path in $isccPaths) {
        if (Test-Path $path) {
            $isccPath = $path
            break
        }
    }
    
    if ($isccPath) {
        # Run Inno Setup
        & $isccPath "SupplierSelection_Setup.iss"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Installer created successfully" -ForegroundColor Green
            
            # Check installer
            if (Test-Path "installer_output\SupplierSelection_Setup_v1.0.0.exe") {
                $installerSize = (Get-Item "installer_output\SupplierSelection_Setup_v1.0.0.exe").Length / 1MB
                Write-Host "  ✓ Installer: SupplierSelection_Setup_v1.0.0.exe ($([math]::Round($installerSize, 2)) MB)" -ForegroundColor Green
            }
        } else {
            Write-Host "  ✗ Installer build failed!" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠ Inno Setup not found. Skipping installer creation." -ForegroundColor Yellow
        Write-Host "  Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Gray
    }
} else {
    Write-Host "[4/4] Skipping installer creation (--SkipInstaller)" -ForegroundColor Gray
}

Write-Host ""

# ========================================
# Summary
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Build Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Output Locations:" -ForegroundColor White
Write-Host "  • Executable:  dist\SupplierSelection\SupplierSelection.exe" -ForegroundColor Gray

if (-not $SkipInstaller -and (Test-Path "installer_output\SupplierSelection_Setup_v1.0.0.exe")) {
    Write-Host "  • Installer:   installer_output\SupplierSelection_Setup_v1.0.0.exe" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Test the executable in dist\SupplierSelection\" -ForegroundColor Gray
Write-Host "  2. Run the installer to test installation" -ForegroundColor Gray
Write-Host "  3. Distribute to users!" -ForegroundColor Gray
Write-Host ""

Write-Host "✓ Build process completed successfully!" -ForegroundColor Green
Write-Host ""
