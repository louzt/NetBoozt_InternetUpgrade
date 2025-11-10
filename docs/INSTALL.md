# Instalación y Configuración

## 📦 Instalación Completa

### Paso 1: Clonar Repositorio

```powershell
git clone https://github.com/loust/windows-network-optimizer.git
cd windows-network-optimizer
```

### Paso 2: Crear Entorno Virtual

```powershell
python -m venv venv
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
   Add-MpPreference -ExclusionPath "C:\ruta\a\windows-network-optimizer"
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
```

## 🚀 Uso

### Opción 1: GUI (Recomendado)

```powershell
# Como ADMINISTRADOR
python run.py
```

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
