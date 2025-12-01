<#
.SYNOPSIS
    Build NetBoozt using Nuitka compiler for optimized native executables.
    
.DESCRIPTION
    Compiles Python code to C and then to native machine code.
    Results in smaller, faster executables compared to PyInstaller.
    Generates both GUI and CLI executables.
    
.NOTES
    Author: LOUST (www.loust.pro)
    Version: 2.2.0
    
.EXAMPLE
    .\build_nuitka.ps1                    # Build both GUI and CLI
    .\build_nuitka.ps1 -Target GUI        # Only GUI
    .\build_nuitka.ps1 -Target CLI        # Only CLI
    .\build_nuitka.ps1 -Version "2.3.0"   # Custom version
#>

param(
    [string]$Version = "2.2.0",
    [ValidateSet("All", "GUI", "CLI")]
    [string]$Target = "All",
    [switch]$OneFile = $true,
    [switch]$Debug = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
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
$DistDir = Join-Path $ProjectRoot "releases\windows"
$BuildCacheDir = Join-Path $ProjectRoot "build_cache"
$AssetsDir = Join-Path $PythonDir "assets"
$IconPath = Join-Path $AssetsDir "icon.ico"

# Fallback to windows directory if new structure doesn't exist yet
if (-not (Test-Path $PythonDir)) {
    $PythonDir = Join-Path $ProjectRoot "windows"
    $AssetsDir = Join-Path $PythonDir "assets"
    $IconPath = Join-Path $AssetsDir "icon.ico"
}

Write-Header "NetBoozt Nuitka Build v$Version"

# Check prerequisites
Write-Color "Checking prerequisites..." "Yellow"

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Color "ERROR: Python not found in PATH" "Red"
    exit 1
}
Write-Color "  ✓ Python: $($python.Source)" "Green"

# Check Nuitka
$nuitkaInstalled = python -c "import nuitka; print('ok')" 2>$null
if ($nuitkaInstalled -ne "ok") {
    Write-Color "  Installing Nuitka..." "Yellow"
    pip install nuitka ordered-set zstandard
}
Write-Color "  ✓ Nuitka installed" "Green"

# Check for C compiler
$hasVS = Test-Path "C:\Program Files\Microsoft Visual Studio"
$hasMingw = Get-Command gcc -ErrorAction SilentlyContinue
if (-not $hasVS -and -not $hasMingw) {
    Write-Color "WARNING: No C compiler found. Nuitka will download MinGW64." "Yellow"
}

# Create directories
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}
if (-not (Test-Path $BuildCacheDir)) {
    New-Item -ItemType Directory -Path $BuildCacheDir -Force | Out-Null
}

# Function to build a target
function Build-Target {
    param(
        [string]$EntryPoint,
        [string]$OutputName,
        [string]$Description,
        [bool]$ShowConsole
    )
    
    Write-Header "Building $Description"
    
    # Base arguments
    $nuitkaArgs = @(
        "-m", "nuitka"
        "--standalone"
        "--enable-plugin=tk-inter"
        "--windows-company-name=LOUST"
        "--windows-product-name=NetBoozt"
        "--windows-file-version=$Version.0"
        "--windows-product-version=$Version.0"
        "--windows-file-description=$Description by LOUST"
        "--output-dir=$BuildCacheDir"
    )
    
    # Console mode based on target type
    if ($ShowConsole) {
        $nuitkaArgs += "--windows-console-mode=force"
    } else {
        $nuitkaArgs += "--windows-console-mode=disable"
    }
    
    # Add onefile if requested
    if ($OneFile) {
        $nuitkaArgs += "--onefile"
        $nuitkaArgs += "--output-filename=$OutputName.exe"
    } else {
        $nuitkaArgs += "--output-filename=$OutputName"
    }
    
    # Add icon if exists
    if (Test-Path $IconPath) {
        $nuitkaArgs += "--windows-icon-from-ico=$IconPath"
        Write-Color "  Using icon: $IconPath" "Cyan"
    }
    
    # Include assets (only for GUI)
    if (-not $ShowConsole -and (Test-Path $AssetsDir)) {
        $nuitkaArgs += "--include-data-dir=$AssetsDir=assets"
        Write-Color "  Including assets from: $AssetsDir" "Cyan"
    }
    
    # Debug mode
    if ($Debug) {
        $nuitkaArgs += "--debug"
        Write-Color "  Debug mode enabled" "Yellow"
    }
    
    # Add entry point
    $nuitkaArgs += $EntryPoint
    
    Write-Color "Entry point: $EntryPoint" "Cyan"
    Write-Color "Output: $OutputName.exe" "Cyan"
    Write-Color ""
    
    # Run Nuitka
    $buildStart = Get-Date
    
    try {
        Push-Location $PythonDir
        Write-Color "Running Nuitka compiler..." "Yellow"
        Write-Color "(This may take 5-15 minutes on first run)" "Gray"
        Write-Host ""
        
        & python @nuitkaArgs
        
        if ($LASTEXITCODE -ne 0) {
            throw "Nuitka compilation failed for $OutputName"
        }
    }
    finally {
        Pop-Location
    }
    
    $buildEnd = Get-Date
    $buildDuration = $buildEnd - $buildStart
    
    # Find output in build cache
    $cacheExe = Join-Path $BuildCacheDir "$OutputName.exe"
    if (-not $OneFile) {
        $cacheExe = Join-Path $BuildCacheDir "$OutputName.dist" "$OutputName.exe"
    }
    
    # Copy to releases directory
    $finalExe = Join-Path $DistDir "$OutputName.exe"
    
    if (Test-Path $cacheExe) {
        Copy-Item $cacheExe $finalExe -Force
        $fileInfo = Get-Item $finalExe
        $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        
        Write-Color "  ✓ $OutputName.exe built successfully!" "Green"
        Write-Color "    Size: $sizeMB MB" "Cyan"
        Write-Color "    Duration: $($buildDuration.ToString('mm\:ss'))" "Cyan"
        Write-Color "    Location: $finalExe" "Gray"
        return @{
            Name = $OutputName
            Path = $finalExe
            Size = $sizeMB
            Duration = $buildDuration
        }
    } else {
        Write-Color "  ✗ $OutputName.exe not found in build cache" "Red"
        return $null
    }
}

# Build targets
$results = @()
$startTime = Get-Date

# GUI Build
if ($Target -eq "All" -or $Target -eq "GUI") {
    $guiEntry = Join-Path $PythonDir "run_modern.py"
    $result = Build-Target -EntryPoint $guiEntry -OutputName "NetBoozt_GUI" -Description "NetBoozt GUI Application" -ShowConsole $false
    if ($result) { $results += $result }
}

# CLI Build
if ($Target -eq "All" -or $Target -eq "CLI") {
    $cliEntry = Join-Path $PythonDir "netboozt_cli.py"
    $result = Build-Target -EntryPoint $cliEntry -OutputName "NetBoozt_CLI" -Description "NetBoozt CLI Application" -ShowConsole $true
    if ($result) { $results += $result }
}

$endTime = Get-Date
$totalDuration = $endTime - $startTime

# Summary
Write-Header "Build Summary"

if ($results.Count -gt 0) {
    Write-Color "✓ Successfully built $($results.Count) executable(s):" "Green"
    Write-Host ""
    
    $totalSize = 0
    foreach ($r in $results) {
        Write-Color "  📦 $($r.Name).exe" "Cyan"
        Write-Color "     Path: $($r.Path)" "Gray"
        Write-Color "     Size: $($r.Size) MB" "Gray"
        $totalSize += $r.Size
    }
    
    Write-Host ""
    Write-Color "  Total size: $totalSize MB" "Yellow"
    Write-Color "  Total time: $($totalDuration.ToString('mm\:ss'))" "Yellow"
    Write-Host ""
    
    # Distribution info
    Write-Color "📁 Output directory: $DistDir" "Cyan"
    Write-Host ""
    Write-Color "Executables:" "Yellow"
    Write-Color "  NetBoozt_GUI.exe - Graphical interface with system tray" "Gray"
    Write-Color "  NetBoozt_CLI.exe - Command-line interface for advanced users" "Gray"
} else {
    Write-Color "✗ No executables were built successfully" "Red"
    exit 1
}

Write-Host ""
