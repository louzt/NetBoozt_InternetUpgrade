# NetBoozt - Build Script with Verification
# Compila la aplicación a .exe con PyInstaller + verificación previa

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         NetBoozt - Build to EXE + Verification               ║" -ForegroundColor Cyan
Write-Host "║         By LOUST (www.loust.pro)                             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "netboozt.spec")) {
    Write-Host "❌ Error: Ejecuta este script desde L:\NetworkFailover\NetBoozt\windows\" -ForegroundColor Red
    exit 1
}

# Paso 0: VERIFICACIÓN PRE-BUILD
Write-Host "🔍 Paso 0: Verificación pre-build..." -ForegroundColor Magenta
python verify_build.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ VERIFICACIÓN FALLÓ - Build cancelado" -ForegroundColor Red
    Write-Host "Corrige los errores mostrados arriba y vuelve a intentar.`n" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Verificación completa`n" -ForegroundColor Green

# Paso 1: Instalar dependencias
Write-Host "📦 Paso 1: Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias instaladas`n" -ForegroundColor Green
} else {
    Write-Host "❌ Error instalando dependencias" -ForegroundColor Red
    exit 1
}

# Paso 2: Limpiar builds anteriores
Write-Host "🧹 Paso 2: Limpiando builds anteriores..." -ForegroundColor Yellow
Remove-Item -Path "build", "dist" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✅ Limpieza completa`n" -ForegroundColor Green

# Paso 3: Compilar con PyInstaller
Write-Host "🔨 Paso 3: Compilando NetBoozt.exe..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 2-3 minutos)`n" -ForegroundColor Gray

python -m PyInstaller netboozt.spec --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ ¡Compilación exitosa!" -ForegroundColor Green
    Write-Host "`n📍 El archivo NetBoozt.exe está en:" -ForegroundColor Cyan
    Write-Host "   $(Get-Location)\dist\NetBoozt.exe`n" -ForegroundColor White
    
    # Verificar tamaño
    $exePath = "dist\NetBoozt.exe"
    if (Test-Path $exePath) {
        $size = (Get-Item $exePath).Length / 1MB
        Write-Host "📊 Tamaño: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
    }
    
    # Copiar al repo principal automáticamente
    $repoRoot = Split-Path (Get-Location) -Parent
    Copy-Item "dist\NetBoozt.exe" "$repoRoot\NetBoozt.exe" -Force
    Write-Host "✅ Copiado al repo principal: $repoRoot\NetBoozt.exe" -ForegroundColor Green
    
    # Preguntar si copiar al Desktop
    Write-Host "`n¿Copiar al Desktop? (S/N): " -ForegroundColor Yellow -NoNewline
    $copy = Read-Host
    
    if ($copy -eq "S" -or $copy -eq "s") {
        $desktop = [Environment]::GetFolderPath("Desktop")
        Copy-Item "dist\NetBoozt.exe" "$desktop\NetBoozt.exe" -Force
        Write-Host "✅ Copiado a Desktop" -ForegroundColor Green
    }
    
} else {
    Write-Host "`n❌ Error en la compilación" -ForegroundColor Red
    Write-Host "Revisa los logs arriba para más detalles" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n🚀 ¡Listo! Ejecuta NetBoozt.exe como Administrador" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
