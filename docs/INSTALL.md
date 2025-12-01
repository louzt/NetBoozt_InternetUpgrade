# 📦 Instalación y Configuración - NetBoozt v2.1

## 🚀 Instalación Rápida

### Paso 1: Clonar Repositorio

```powershell
git clone https://github.com/louzt/NetBoozt_InternetUpgrade.git
cd NetBoozt_InternetUpgrade/windows
```

### Paso 2: Crear Entorno Virtual

```powershell
python -m venv venv --copies
```

**⚠️ PROBLEMA COMÚN: Antivirus bloquea venv**

Si tu antivirus (Avast, Windows Defender, etc.) bloquea la creación:

1. **Avast:**
   - Abre Avast
   - Menú → Configuración → General → Excepciones
   - Agregar excepción → Ruta de carpeta
   - Selecciona la carpeta del proyecto

2. **Windows Defender:**
   ```powershell
   # Como administrador
   Add-MpPreference -ExclusionPath "L:\NetworkFailover\NetBoozt\windows"
   ```

### Paso 3: Activar Entorno

```powershell
.\venv\Scripts\Activate.ps1
```

**Si aparece error "execution of scripts is disabled":**

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Paso 4: Instalar Dependencias

```powershell
pip install --upgrade pip
pip install -r requirements.txt

# OPCIONAL: Notificaciones de Windows (altamente recomendado)
pip install winotify
```

**Dependencias instaladas:**
- `customtkinter` - UI moderna
- `psutil` - Monitoreo de red
- `tinydb` - Base de datos local
- `matplotlib` - Gráficas avanzadas
- `pillow` - Manejo de imágenes
- `winotify` - Notificaciones Windows (opcional)

## 🚀 Uso

### Opción 1: GUI Moderna (Recomendado)

```powershell
# Como ADMINISTRADOR (REQUERIDO)
python run.py
```

**Primer Uso:**
1. La aplicación detecta automáticamente optimizaciones ya aplicadas
2. Revisa las optimizaciones sugeridas (pre-seleccionadas)
3. Haz clic en "✅ Aplicar Optimizaciones" (crea backup automáticamente)
4. Explora las 12 pestañas disponibles:
   - 📊 **Dashboard**: Monitoreo en tiempo real
   - 🚀 **Optimizaciones**: Aplicar/revertir cambios TCP
   - 📈 **Estado de Red**: Métricas actuales
   - 🔄 **Failover DNS**: Configurar auto-failover
   - 📊 **Gráficas**: 4 gráficas con zoom temporal
   - 🔔 **Alertas**: Configurar thresholds
   - 💾 **Backups**: Crear/restaurar snapshots
   - ⚙️ **Configuración**: Tema, autostart, etc.
   - ℹ️ **About**: Información del proyecto
   - 📄 **README**: Documentación rápida
   - 📖 **Documentación**: Guías técnicas
   - 🔗 **GitHub**: Enlaces del proyecto

### Opción 2: CLI

```powershell
python -c "from src.optimizations.network_optimizer import *; opt = WindowsNetworkOptimizer(); opt.apply_profile(OptimizationLevel.BALANCED)"
```

### Opción 3: Script Personalizado

```python
from src.optimizations.network_optimizer import WindowsNetworkOptimizer

# Crear optimizador
optimizer = WindowsNetworkOptimizer()

# Ver todas las optimizaciones
print(optimizer.generate_report())

# Aplicar solo algunas
optimizer.apply_optimization('tcp_congestion')
optimizer.apply_optimization('rss')
optimizer.apply_optimization('ecn')
```

## 🆕 Características v2.1 (Nuevas)

### 1. DNS Auto-Failover

**Activar:**
1. Ve a la pestaña "Failover DNS"
2. Activa el switch "Habilitar Auto-Failover"
3. El sistema monitorea automáticamente cada 15s
4. Cambia de tier si detecta fallas (cooldown de 60s)

**Configuración:**
```python
# Los 7 tiers están pre-configurados:
Tier 1: Cloudflare (1.1.1.1)
Tier 2: Google (8.8.8.8)
Tier 3: Quad9 (9.9.9.9)
Tier 4: OpenDNS (208.67.222.222)
Tier 5: Adguard (94.140.14.14)
Tier 6: Cloudflare Family (1.1.1.3)
Tier 7: DHCP (tu router)
```

### 2. Sistema de Alertas

**Configurar Thresholds:**
1. Ve a la pestaña "Alertas"
2. Configura valores límite:
   - Latencia Alta: 100ms (default)
   - Pérdida de Paquetes: 2% (default)
   - Velocidad Baja: 10 Mbps (default)
3. Haz clic en "Guardar Configuración"

**Alertas se muestran:**
- En la pestaña Alertas (historial)
- Como notificaciones de Windows
- Con cooldown para evitar spam

### 3. Backups de Configuración

**Crear Backup:**
1. Ve a la pestaña "Backups"
2. Haz clic en "📸 Crear Backup Ahora"
3. El snapshot incluye:
   - Servidores DNS
   - Configuración IP
   - Settings TCP globales
   - Valores del registro

**Restaurar:**
1. Selecciona un backup de la lista
2. Haz clic en "↩️ Restaurar"
3. Confirmación instantánea

**Ubicación:** `C:\Users\<tu_usuario>\.netboozt\backups\`

### 4. Gráficas Avanzadas

**Usar Zoom Temporal:**
1. Ve a la pestaña "Gráficas"
2. Selecciona rango: 5min, 15min, 30min, 1h, 6h, 24h, 7 días
3. Las 4 gráficas se actualizan en tiempo real:
   - Velocidad de Descarga
   - Velocidad de Subida
   - Latencia
   - Pérdida de Paquetes

**Almacenamiento Inteligente:**
- Últimas 24h: TODO
- 1-7 días: 1 sample/hora
- 8-30 días: 1 sample/día
- 30+ días: 1 sample/semana

### 5. Dark/Light Theme

**Cambiar Tema:**
1. Ve a "Configuración"
2. Haz clic en el botón de tema (🌙/☀️)
3. La interfaz se actualiza instantáneamente

## 🔧 Configuración Avanzada

### Personalizar Optimizaciones

Edita `src/optimizations/network_optimizer.py`:

```python
# Cambiar valor optimizado
self.optimizations['initialrto'] = NetworkOptimization(
    name="Initial RTO",
    optimized_value="2000",  # Cambiar de 1000ms a 2000ms
    # ...
)
```

### Crear Tu Propio Perfil

```python
def apply_my_custom_profile(self) -> Dict[str, bool]:
    """Mi perfil personalizado"""
    custom_opts = [
        'tcp_congestion',
        'rss',
        'ecn',
        'fastopen',
        'hystart'
    ]
    
    results = {}
    for opt_id in custom_opts:
        results[opt_id] = self.apply_optimization(opt_id)
    
    return results
```

## 📊 Verificar Configuración Actual

```powershell
# Ver configuración TCP global
netsh int tcp show global

# Ver configuración específica
Get-NetTCPSetting | Format-List *

# Ver adaptadores de red
Get-NetAdapter | Format-Table Name, Status, LinkSpeed
```

## 🔄 Restaurar Configuración

### Desde GUI
Click en "Restaurar Defaults"

### Desde CLI
```powershell
python -c "from src.optimizations.network_optimizer import *; WindowsNetworkOptimizer().reset_to_defaults()"
```

### Manual
```powershell
# Como administrador
netsh int tcp reset
netsh winsock reset

# Reiniciar
Restart-Computer
```

## 🧪 Testing

```powershell
# Instalar pytest
pip install pytest pytest-cov

# Ejecutar tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html
```

## 📝 Notas Importantes

1. **Permisos de Administrador:** Requeridos para aplicar cambios
2. **Reinicio:** Algunas optimizaciones requieren reiniciar
3. **Hardware:** Algunas features requieren soporte de hardware (ej: RSS)
4. **Reversible:** Siempre puedes restaurar a defaults

## 🐛 Problemas Comunes

### Error: "No module named 'src'"

```powershell
# Asegúrate de estar en la carpeta correcta
cd windows-network-optimizer

# Ejecuta con python -m
python -m src.gui.main_window
```

### GUI no se ve moderna

```powershell
# Instalar ttkbootstrap
pip install ttkbootstrap
```

### "Access Denied"

- Ejecuta PowerShell como **Administrador**
- Click derecho en PowerShell → "Ejecutar como administrador"

## 📚 Recursos Adicionales

- [Documentación de netsh](https://docs.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh)
- [TCP Tuning Guide](https://docs.microsoft.com/en-us/windows-server/networking/technologies/network-subsystem/net-sub-performance-tuning-nics)
- [BBR Paper (Google)](https://queue.acm.org/detail.cfm?id=3022184)
