---
applyTo: '**'
---

# NetBoozt - Instrucciones para AI/LLM/Copilot

> Este archivo proporciona contexto y guías para asistentes de código AI cuando trabajan con el proyecto NetBoozt.

---

## 📋 Información del Proyecto

| Campo | Valor |
|-------|-------|
| **Nombre** | NetBoozt |
| **Tipo** | Aplicación de escritorio Windows (Network Optimization Tool) |
| **Versión** | 2.2.x |
| **Lenguaje** | Python 3.11+ (migrando a Rust/Tauri en v3.0) |
| **GUI Framework** | CustomTkinter |
| **Licencia** | MIT (opensource) / Propietaria (versión LOUST) |
| **Autor** | LOUST (www.loust.pro) |

---

## 🎯 Funcionalidades Principales

### Optimizaciones TCP/IP (BBR-like para Windows)

| Optimización | Descripción | Comando |
|--------------|-------------|---------|
| **TCP Congestion Control** | Algoritmo similar a BBR de Linux | `netsh int tcp set supplemental Template=Internet CongestionProvider=NewReno` |
| **HyStart++** | Slow-start rápido, sale temprano para evitar queue buildup | Registry: `EnableHyStart=1` |
| **PRR** | Proportional Rate Reduction - recuperación suave de pérdidas | Registry: `EnablePrr=1` |
| **ECN** | Explicit Congestion Notification - detecta congestión sin pérdidas | `netsh int tcp set global ecncapability=enabled` |
| **TCP Fast Open** | Envía datos en SYN, ahorra 1 RTT | Registry: `EnableTFO=1` |
| **TCP Pacing** | Envío suave de paquetes (como BBR) | Registry: `EnableWsd=0` |
| **RSS** | Receive Side Scaling - multi-CPU para paquetes | `netsh int tcp set global rss=enabled` |
| **RSC** | Receive Segment Coalescing - combina segmentos TCP | `netsh int tcp set global rsc=enabled` |
| **TCP Autotuning** | Buffers dinámicos hasta 16MB | `netsh int tcp set global autotuninglevel=normal` |
| **Initial RTO** | Timeout inicial reducido (3s→1s) | Registry: `TcpInitialRto=1000` |

### Perfiles de Optimización

| Perfil | Optimizaciones | Riesgo |
|--------|----------------|--------|
| 🟢 **Conservador** | RSS, RSC, Autotuning básico | Mínimo |
| 🟡 **Balanceado** | + HyStart++, PRR, ECN, Fast Open | Bajo |
| 🔴 **Agresivo** | + Pacing, Initial RTO, todas | Medio |

### Sistema de Monitoreo

| Feature | Descripción |
|---------|-------------|
| **Real-time Monitor** | Métricas de red en vivo (download, upload, latencia) |
| **DNS Health Check** | Verificación real de resolución DNS (no solo ping) |
| **Auto-Failover DNS** | Cambio automático entre 8 tiers de DNS |
| **Windows Event Log** | Monitoreo de eventos DNS-Client, WLAN, NCSI, DHCP, Tcpip |
| **4-Phase Diagnostics** | Adapter → Router → ISP → DNS |
| **Alert System** | Notificaciones configurables (toast, sound) |

### Jerarquía DNS (8 Tiers)

```
Tier 1: Cloudflare     (1.1.1.1)      ← Más rápido
Tier 2: Google         (8.8.8.8)      ← Más confiable
Tier 3: Quad9          (9.9.9.9)      ← Seguridad
Tier 4: OpenDNS        (208.67.222.222)
Tier 5: AdGuard        (94.140.14.14) ← Ad-blocking
Tier 6: CleanBrowsing  (185.228.168.9)
Tier 7: Router/DHCP    (Auto)         ← ISP fallback
Tier 8: ISP Detected   (Auto-detect)  ← DNS del proveedor
```

---

## 🏗️ Estructura del Proyecto (v2.2+)

```
NetBoozt/
├── platforms/                  # Código específico por plataforma
│   ├── python/                 # Versión Python actual (v2.x)
│   │   ├── src/                # Código fuente Python
│   │   │   ├── core/           # Lógica central
│   │   │   ├── gui/            # Interfaz CustomTkinter
│   │   │   ├── monitoring/     # Monitoreo de red
│   │   │   ├── optimizations/  # Optimizaciones TCP/IP
│   │   │   ├── storage/        # Persistencia (TinyDB)
│   │   │   └── utils/          # Utilidades
│   │   ├── assets/             # Imágenes, iconos
│   │   ├── tests/              # Tests Python
│   │   ├── requirements.txt
│   │   ├── run_modern.py       # Entry point GUI
│   │   └── netboozt_cli.py     # CLI interactivo
│   │
│   ├── tauri/                  # Versión Tauri (v3.0 - futuro)
│   │   ├── src-tauri/          # Backend Rust
│   │   └── src/                # Frontend Web (Svelte)
│   │
│   └── linux/                  # Versión Linux (futuro)
│
├── shared/                     # Configuración compartida
│   ├── dns_servers.json        # Lista de DNS servers
│   ├── optimizations.json      # Definiciones de optimizaciones
│   └── translations/           # i18n
│
├── scripts/                    # Scripts de build
│   ├── build_nuitka.ps1        # Build con Nuitka (recomendado)
│   ├── build_python.ps1        # Build con PyInstaller
│   └── dev.ps1                 # Modo desarrollo
│
├── docs/                       # Documentación
│   ├── architecture/           # Arquitectura y decisiones
│   │   └── LANGUAGE_DECISION.md
│   ├── optimizations/          # Docs técnicos
│   ├── es/                     # Docs en español
│   └── assets/
│
├── windows/                    # LEGACY - migrar a platforms/python
│   └── ...
│
└── tools/                      # Herramientas de desarrollo
```

### Nota de Migración
El código en `windows/` se migrará gradualmente a `platforms/python/`. Los scripts de build soportan ambas ubicaciones durante la transición.

---

## 🔧 Módulos Principales

### `src/monitoring/` - Sistema de Monitoreo

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| `adapter_manager.py` | Gestión de adaptadores de red Windows | ✅ Estable |
| `realtime_monitor.py` | Métricas de red en tiempo real | ✅ Estable |
| `dns_health.py` | Health check de servidores DNS con resolución real | ✅ v2.2 mejorado |
| `auto_failover.py` | Cambio automático de DNS (8 tiers) | ✅ v2.2 mejorado |
| `alert_system.py` | Sistema de alertas configurables | ✅ Estable |
| `windows_events.py` | Lectura de Windows Event Log (DNS, WLAN, NCSI) | ✅ v2.2 nuevo |
| `network_diagnostics.py` | Diagnóstico de 4 fases (Adapter→Router→ISP→DNS) | ✅ v2.2 nuevo |

### `src/gui/` - Interfaz Gráfica

| Archivo | Propósito |
|---------|-----------|
| `main_window.py` | Ventana principal y tabs (12+ tabs) |
| `modern_window.py` | Implementación moderna con CustomTkinter |
| `dashboard.py` | Panel de métricas en vivo |
| `theme_manager.py` | Gestión de temas dark/light |
| `advanced_graphs.py` | Gráficas con matplotlib |
| `about_tab.py` | Tab de información y créditos |
| `splash_screen.py` | Pantalla de inicio |

### `src/optimizations/` - Optimizaciones de Red

| Archivo | Propósito |
|---------|-----------|
| `optimizer.py` | Aplicación de optimizaciones (perfiles) |
| `detection.py` | Detección de estado actual del sistema |
| `network_optimizer.py` | 15+ optimizaciones TCP/IP definidas |

### `src/storage/` - Persistencia

| Archivo | Propósito |
|---------|-----------|
| `db_manager.py` | Base de datos TinyDB |
| `backup_system.py` | Backups de configuración de red |
| `speed_test_storage.py` | Almacenamiento de speed tests |

---

## 🔌 APIs de Windows Utilizadas

### PowerShell Commands

```powershell
# Adaptadores de red
Get-NetAdapter | Where-Object Status -eq 'Up' | Select-Object Name, InterfaceDescription, Status, LinkSpeed

# Cambiar DNS
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ServerAddresses 1.1.1.1,1.0.0.1

# Resetear DNS a DHCP
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ResetServerAddresses

# Flush DNS cache
Clear-DnsClientCache

# Ver configuración TCP
netsh int tcp show global

# Obtener gateway
(Get-NetRoute -DestinationPrefix '0.0.0.0/0').NextHop

# Windows Event Log (DNS)
Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-DNS-Client'} -MaxEvents 100
```

### Event Log Providers

| Provider | Eventos |
|----------|---------|
| `Microsoft-Windows-DNS-Client` | DNS timeouts, resolution failures |
| `Microsoft-Windows-WLAN-AutoConfig` | WiFi disconnects, signal issues |
| `Microsoft-Windows-NCSI` | Network connectivity status |
| `Microsoft-Windows-Dhcp-Client` | DHCP lease issues |
| `Tcpip` | TCP/IP stack events |

### Estilo Python

```python
# Imports ordenados: stdlib, third-party, local
import os
import subprocess
from typing import Dict, List, Optional

import customtkinter as ctk
from PIL import Image

from ..utils.logger import log_info, log_error

# Docstrings en español o inglés (consistente por archivo)
def funcion_ejemplo(parametro: str) -> bool:
    """
    Descripción breve de la función.
    
    Args:
        parametro: Descripción del parámetro
    
    Returns:
        True si éxito, False si fallo
    """
    pass

# Clases con docstring
class MiClase:
    """Descripción de la clase y su propósito."""
    
    def __init__(self):
        self._private_var = None  # Underscore para privadas
        self.public_var = None
```

### Logging (NO usar print)

```python
from ..utils.logger import log_info, log_warning, log_error

# ✅ Correcto
log_info("Operación completada")
log_warning("Advertencia: algo puede fallar")
log_error("Error crítico", exception)

# ❌ Incorrecto
print("Debug message")
```

### Manejo de Excepciones

```python
# ✅ Correcto - excepciones específicas
try:
    resultado = operacion_red()
except subprocess.TimeoutExpired:
    log_warning("Timeout en operación")
except PermissionError:
    log_error("Sin permisos de administrador")
except Exception as e:
    log_error(f"Error inesperado: {e}")

# ❌ Incorrecto - except genérico sin tipo
try:
    algo()
except:
    pass
```

### Thread Safety

```python
import threading

class MonitorSeguro:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {}
    
    def get_data(self):
        with self._lock:
            return dict(self._data)  # Retornar copia
    
    def set_data(self, key, value):
        with self._lock:
            self._data[key] = value
```

### Comandos PowerShell

```python
import subprocess

def run_powershell(command: str) -> str:
    """Ejecutar comando PowerShell sin ventana visible."""
    result = subprocess.run(
        ["powershell", "-Command", command],
        capture_output=True,
        text=True,
        timeout=10,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    return result.stdout.strip()
```

---

## 🎨 Convenciones GUI (CustomTkinter)

### Colores del Tema

```python
# Tema Oscuro
DARK_THEME = {
    'bg': '#1a1a1a',
    'card': '#2b2b2b',
    'text': '#ffffff',
    'accent': '#00d4aa',  # Verde LOUST
    'error': '#ff4444',
    'warning': '#ffaa00',
    'success': '#00d4aa',
}

# Tema Claro
LIGHT_THEME = {
    'bg': '#f0f0f0',
    'card': '#ffffff',
    'text': '#1a1a1a',
    'accent': '#0078d4',
}
```

### Componentes Comunes

```python
import customtkinter as ctk

# Botón estándar
btn = ctk.CTkButton(
    parent,
    text="Texto",
    command=callback,
    fg_color="#00d4aa",
    hover_color="#00b894",
    corner_radius=8
)

# Label con estilo
label = ctk.CTkLabel(
    parent,
    text="Título",
    font=("Segoe UI", 16, "bold"),
    text_color="#ffffff"
)

# Frame/Card
card = ctk.CTkFrame(
    parent,
    fg_color="#2b2b2b",
    corner_radius=12
)
```

---

## 🔌 APIs de Red Windows

### Obtener Adaptadores

```python
# PowerShell para obtener adaptadores activos
Get-NetAdapter | Where-Object Status -eq 'Up' | 
    Select-Object Name, InterfaceDescription, Status, LinkSpeed
```

### Cambiar DNS

```python
# Establecer DNS estático
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ServerAddresses 1.1.1.1,1.0.0.1

# Resetear a DHCP
Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ResetServerAddresses

# Limpiar caché DNS
ipconfig /flushdns
```

### Optimizaciones TCP

```python
# Ver configuración actual
Get-NetTCPSetting | Select-Object SettingName, CongestionProvider

# Habilitar ECN
Set-NetTCPSetting -SettingName InternetCustom -EcnCapability Enabled
```

---

## 📝 Patrones Comunes

### Singleton para Managers

```python
_instance = None

def get_manager() -> Manager:
    """Obtener instancia única del manager."""
    global _instance
    if _instance is None:
        _instance = Manager()
    return _instance
```

### Callbacks y Eventos

```python
class Monitor:
    def __init__(self):
        self._callbacks = []
    
    def on_event(self, callback):
        """Registrar callback para eventos."""
        self._callbacks.append(callback)
    
    def _notify(self, event):
        """Notificar todos los callbacks."""
        for cb in self._callbacks:
            try:
                cb(event)
            except Exception as e:
                log_error(f"Error en callback: {e}")
```

### Background Threads

```python
import threading

class BackgroundService:
    def __init__(self):
        self.is_running = False
        self._thread = None
    
    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _loop(self):
        while self.is_running:
            try:
                self._do_work()
            except Exception as e:
                log_error(f"Error en loop: {e}")
            time.sleep(self.interval)
```

---

## 🚫 Anti-Patrones (Evitar)

```python
# ❌ NO: Print para debugging
print(f"Debug: {variable}")

# ❌ NO: Except genérico
except:
    pass

# ❌ NO: Hardcodear rutas
path = "C:\\Users\\Usuario\\Desktop\\file.txt"

# ❌ NO: Bloquear UI con operaciones largas
def on_button_click():
    resultado = operacion_lenta()  # Bloquea UI

# ❌ NO: Variables globales mutables
datos_globales = []

# ❌ NO: Ignorar thread safety
self.data[key] = value  # Sin lock
```

---

## ✅ Buenas Prácticas

```python
# ✅ SÍ: Usar logger
log_info(f"Operación: {variable}")

# ✅ SÍ: Excepciones específicas
except subprocess.TimeoutExpired as e:
    log_warning(f"Timeout: {e}")

# ✅ SÍ: Rutas relativas o dinámicas
path = Path(__file__).parent / "assets" / "file.txt"

# ✅ SÍ: Background thread para operaciones largas
def on_button_click():
    threading.Thread(target=operacion_lenta, daemon=True).start()

# ✅ SÍ: Configuración en clase o archivo
class Config:
    DNS_SERVERS = ["1.1.1.1", "8.8.8.8"]

# ✅ SÍ: Thread safety con locks
with self._lock:
    self.data[key] = value
```

---

## 🔄 Flujo de Desarrollo

### Agregar Nueva Característica

1. Crear módulo en carpeta apropiada (`monitoring/`, `gui/`, etc.)
2. Agregar exports en `__init__.py` del módulo
3. Implementar con logging apropiado
4. Agregar tests si aplica
5. Actualizar documentación en `docs/`
6. Probar con `python run_modern.py`

### Compilar Ejecutable

```powershell
# Opción 1: Nuitka (recomendado - más pequeño y rápido)
.\scripts\build_nuitka.ps1

# Opción 2: PyInstaller (legacy)
.\scripts\build_python.ps1

# Opción 3: CLI interactivo
cd windows
python netboozt_cli.py
# Opción 1 (Build) o 3 (Rebuild)
```

### Modo Desarrollo

```powershell
# Ejecutar GUI directamente
.\scripts\dev.ps1

# Ejecutar CLI
.\scripts\dev.ps1 -CLI

# Ejecutar tests
.\scripts\dev.ps1 -Test
```

---

## 📚 Referencias

### Documentación del Proyecto

> Rutas relativas desde la raíz del proyecto (`NetBoozt/`)

- `docs/architecture/LANGUAGE_DECISION.md` - Rust/Tauri vs Python
- `docs/optimizations/bbr-vs-cubic.md` - Comparación de algoritmos
- `docs/optimizations/tcp-congestion-control.md` - Detalles técnicos
- `docs/WHATS_NEW_V2.2.md` - Changelog detallado

### Recursos Externos

- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [Nuitka User Manual](https://nuitka.net/doc/user-manual.html)
- [Tauri Documentation](https://tauri.app/v1/guides/)
- [Windows PowerShell Network Commands](https://docs.microsoft.com/en-us/powershell/module/nettcpip/)

### Archivos de Configuración Compartidos

- `shared/dns_servers.json` - Servidores DNS y tiers
- `shared/optimizations.json` - Definiciones de optimizaciones

---

## 🗺️ Roadmap

### v2.x (Python + Nuitka)
- ✅ v2.2: Windows Event Log, 4-Phase Diagnostics, DNS mejorado
- 🔄 v2.3: Integración GUI de diagnósticos, ISP DNS auto-detect
- 📋 v2.4: Gráficas históricas, scoring de calidad de red

### v3.0 (Rust + Tauri)
- 📋 Backend Rust con windows-rs
- 📋 Frontend SvelteKit
- 📋 Tamaño ~5MB, inicio <0.5s

---

## 🤝 Contribuir

1. Fork del repositorio
2. Crear branch: `feature/mi-caracteristica`
3. Seguir convenciones de este documento
4. Pull request con descripción clara

**Contacto:** opensource@loust.pro  
**Website:** www.loust.pro  
**GitHub:** github.com/louzt/NetBoozt_InternetUpgrade
