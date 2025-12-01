<#
.SYNOPSIS
    Build NetBoozt using PyInstaller (current method).
    
.DESCRIPTION
    Creates a standalone executable using PyInstaller.
    This is the current build method for v2.x releases.
    
.NOTES
    Author: LOUST (www.loust.pro)
    Version: 2.2.0
    
.EXAMPLE
    .\build_python.ps1
    .\build_python.ps1 -Clean
#>

param(
    [switch]$Clean = $false,
    [switch]$OneFile = $true,
    [switch]$Console = $false
)

$ErrorActionPreference = "Stop"

function Write-Color {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
}

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonDir = Join-Path $ProjectRoot "platforms\python"

# Fallback to windows directory if new structure doesn't exist yet
if (-not (Test-Path $PythonDir)) {
    $PythonDir = Join-Path $ProjectRoot "windows"
}

$DistDir = Join-Path $PythonDir "dist"
$BuildDir = Join-Path $PythonDir "build"
$SpecFile = Join-Path $PythonDir "netboozt.spec"

Write-Header "NetBoozt PyInstaller Build"

# Clean if requested
if ($Clean) {
    Write-Color "Cleaning previous builds..." "Yellow"
    if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
    if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
    Write-Color "  ✓ Cleaned" "Green"
}

# Check prerequisites
Write-Color "Checking prerequisites..." "Yellow"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Color "ERROR: Python not found" "Red"
    exit 1
}
Write-Color "  ✓ Python: $($python.Source)" "Green"

# Check PyInstaller
$pyinstallerInstalled = python -c "import PyInstaller; print('ok')" 2>$null
if ($pyinstallerInstalled -ne "ok") {
    Write-Color "  Installing PyInstaller..." "Yellow"
    pip install pyinstaller
}
Write-Color "  ✓ PyInstaller installed" "Green"

# Install dependencies
Write-Color "Installing dependencies..." "Yellow"
$reqFile = Join-Path $PythonDir "requirements.txt"
if (Test-Path $reqFile) {
    pip install -r $reqFile --quiet
    Write-Color "  ✓ Dependencies installed" "Green"
}

# Build
Write-Header "Building with PyInstaller"

$startTime = Get-Date

try {
    Push-Location $PythonDir
    
    if (Test-Path $SpecFile) {
        Write-Color "Using spec file: $SpecFile" "Cyan"
        pyinstaller $SpecFile --noconfirm
    } else {
        Write-Color "No spec file found, using default options" "Yellow"
        $args = @("run_modern.py", "--name", "netboozt", "--noconfirm")
        if ($OneFile) { $args += "--onefile" }
        if (-not $Console) { $args += "--windowed" }
        pyinstaller @args
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Header "Build Complete"

# Find output
$outputExe = Join-Path $DistDir "netboozt.exe"
if (-not (Test-Path $outputExe)) {
    $outputExe = Join-Path $DistDir "netboozt" "netboozt.exe"
}

if (Test-Path $outputExe) {
    $fileInfo = Get-Item $outputExe
    $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    
    Write-Color "  ✓ Build successful!" "Green"
    Write-Color "  Output: $outputExe" "Cyan"
    Write-Color "  Size: $sizeMB MB" "Cyan"
    Write-Color "  Duration: $($duration.ToString('mm\:ss'))" "Cyan"
} else {
    Write-Color "  ✗ Output not found" "Red"
    exit 1
}

Write-Host ""
Write-Color "Run with: & '$outputExe'" "Cyan"
Write-Host ""
