@echo off
REM NetBoozt CLI Launcher
REM By LOUST (www.loust.pro)

title NetBoozt CLI
cd /d "%~dp0"

echo.
echo ========================================
echo    NetBoozt Development CLI
echo    By LOUST (www.loust.pro)
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado
    echo Instala Python 3.13+ desde python.org
    echo.
    pause
    exit /b 1
)

REM Verificar si ya tiene admin
net session >nul 2>&1

if %errorlevel% == 0 (
    echo [ADMIN MODE ACTIVE]
    echo.
    REM Ya tiene admin - ejecutar directamente
    python netboozt_cli.py
    if %errorlevel% neq 0 (
        echo.
        echo Error al ejecutar CLI
        pause
    )
) else (
    echo [Standard Mode - Some features require admin]
    echo Requesting administrator privileges...
    echo.
    REM Solicitar admin usando PowerShell
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && netboozt.bat' -Verb RunAs"
)
