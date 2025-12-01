<#
.SYNOPSIS
    Development mode for NetBoozt - runs Python code directly.
    
.DESCRIPTION
    Quick development script to run NetBoozt without building.
    Supports running GUI, CLI, or tests.
    
.NOTES
    Author: LOUST (www.loust.pro)
    
.EXAMPLE
    .\dev.ps1           # Run GUI
    .\dev.ps1 -CLI      # Run CLI
    .\dev.ps1 -Test     # Run tests
#>

param(
    [switch]$CLI = $false,
    [switch]$Test = $false,
    [switch]$Install = $false
)

$ErrorActionPreference = "Stop"

function Write-Color {
    param([string]$Text, [string]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonDir = Join-Path $ProjectRoot "platforms\python"

# Fallback to windows directory if new structure doesn't exist yet
if (-not (Test-Path $PythonDir)) {
    $PythonDir = Join-Path $ProjectRoot "windows"
}

# Install dependencies if requested
if ($Install) {
    Write-Color "Installing dependencies..." "Yellow"
    $reqFile = Join-Path $PythonDir "requirements.txt"
    if (Test-Path $reqFile) {
        pip install -r $reqFile
    }
    
    $devReqFile = Join-Path $ProjectRoot "requirements-dev.txt"
    if (Test-Path $devReqFile) {
        pip install -r $devReqFile
    }
    
    Write-Color "✓ Dependencies installed" "Green"
    Write-Host ""
}

# Navigate to Python directory
Push-Location $PythonDir

try {
    if ($Test) {
        Write-Color "Running tests..." "Cyan"
        python -m pytest tests/ -v
    }
    elseif ($CLI) {
        Write-Color "Starting NetBoozt CLI..." "Cyan"
        python netboozt_cli.py
    }
    else {
        Write-Color "Starting NetBoozt GUI..." "Cyan"
        python run_modern.py
    }
}
finally {
    Pop-Location
}
