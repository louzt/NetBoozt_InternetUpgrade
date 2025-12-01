# 🚀 NetBoozt - Sistema de Mejora de Internet

<div align="center">

![NetBoozt Logo](docs/assets/logo/netboozt_icon.png)

**Transforma tu Velocidad de Internet Sin Cambiar de ISP**

[![Versión](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/louzt/NetBoozt_InternetUpgrade)
[![Licencia](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Plataforma](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20WSL-lightgrey.svg)]()
[![PRs Bienvenidos](https://img.shields.io/badge/PRs-bienvenidos-brightgreen.svg)](CONTRIBUTING.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Líneas de Código](https://img.shields.io/badge/l%C3%ADneas-9300%2B-green.svg)]()

**Rendimiento BBR • Auto-Failover DNS • Alertas Inteligentes • Backups de Red • Monitoreo Avanzado**

[English](README.md) | **Español**

[¿Por Qué NetBoozt?](#-la-historia-detrás-de-netboozt) • [Qué Obtienes](#-qué-obtienes) • [Inicio Rápido](#-inicio-rápido) • [Benchmarks](#-cómo-funciona-netboozt)

---

> *"Tenía fibra de 1 Gbps pero solo conseguía 450 Mbps. Mi ISP dijo 'es tu computadora.' Tenían razón—pero no como pensaban."*  
> **— David Mireles ([@lou404x](https://twitter.com/lou404x)), Creador de NetBoozt**

---

**Por [LOUST](https://www.loust.pro/DavidMireles)** | **Contacto**: [opensource@loust.pro](mailto:opensource@loust.pro) | **Twitter/Instagram**: [@lou404x](https://twitter.com/lou404x)

</div>

---

## 💭 La Historia Detrás de NetBoozt

**¿Alguna vez has experimentado esto?**

- 🎮 **Picos de lag en juegos** durante momentos cruciales, incluso con internet "bueno"
- 📉 **Descargas limitadas a 450 Mbps** en una conexión de fibra de 1 Gbps
- 🌐 **WiFi fallando aleatoriamente**, obligándote a cambiar manualmente a Ethernet
- 🔄 **DNS timeout** cuando los servidores de tu ISP se caen
- 📺 **Buffering en streaming 4K** a pesar de tener suficiente ancho de banda
- ⚡ **Ping alto en videollamadas** mientras descargas archivos

**Yo sí. Todos. Los. Días.**

### Mi Viaje

Soy desarrollador con una conexión de fibra de 1 Gbps. En teoría, mi internet debería ser ultrarrápido. Pero la realidad contaba otra historia:

- **Descargas**: Atascadas en 450-500 Mbps (¡50% de capacidad!)
- **Gaming**: Picos de lag aleatorios arruinando partidas competitivas
- **WiFi**: Se caía la conexión, requiriendo cambio manual de adaptador
- **DNS**: Servidores DNS del ISP con timeout frecuente

**La Frustración**: Pagaba por internet premium pero obtenía rendimiento mediocre.

**La Investigación**: Configuré la misma prueba en una VM Linux... y obtuve **850-950 Mbps** en la misma red. ¿La diferencia? Linux usa **BBR** (control de congestión moderno), Windows usa **CUBIC** (algoritmo de 2006).

**El Descubrimiento**:
1. El stack TCP de Windows está **desactualizado** - no ha cambiado significativamente desde Windows 7
2. Failover WiFi/Ethernet es **manual** - sin cambio inteligente
3. Fallback DNS es **inexistente** - una falla del servidor = internet muerto
4. Throttling del ISP **no detectado** - sin monitoreo en tiempo real

**La Solución**: No podía esperar a que Microsoft actualizara Windows. Así que construí NetBoozt.

### Qué Resuelve NetBoozt

✅ **Descargas Lentas**: Optimizaciones tipo BBR → +15-20% throughput  
✅ **Lag en Gaming**: Bufferbloat reducido → -77% latencia durante descargas  
✅ **Fallas de Red**: Failover inteligente Ethernet ↔ WiFi → cambio sin interrupciones  
✅ **Caídas de DNS**: Fallback DNS de 7 niveles → conectividad siempre activa  
✅ **Throttling del ISP**: Monitoreo en tiempo real → detectar y adaptar  

**Resultado**: Pasé de 450 Mbps (frustrado) a 520 Mbps (satisfecho), con gaming estable y cero timeouts de DNS.

**Ahora lo comparto contigo.** 🚀

## 🎯 Qué Obtienes

NetBoozt es tu **solución todo-en-uno de rendimiento de red**:

### 🚀 Optimización TCP/IP (El Núcleo)
Trae **rendimiento tipo BBR de Google** a Windows sin hackear el kernel:
- ✅ **Descargas 15-20% más rápidas** (probado en 100+ conexiones)
- ✅ **77% menor latencia** durante descargas (¡adiós bufferbloat!)
- ✅ **Gaming fluido** incluso descargando (sin picos de lag)
- ✅ **Videollamadas estables** con uploads simultáneos
- ✅ **8 optimizaciones reales** aplicadas vía PowerShell/Registry

### 🔄 Failover Inteligente de Red (NUEVO v2.1)
**Nunca pierdas conexión de nuevo:**
- ✅ **Auto-cambio** entre Ethernet y WiFi cuando uno falla
- ✅ **Handoff sin interrupciones** (tu llamada de Zoom no se caerá)
- ✅ **Prioridades configurables** (Ethernet primero, WiFi respaldo)
- ✅ **Notificaciones toast** cuando ocurre failover

### 🌐 DNS Auto-Failover (Escudo de 7 Niveles + Health Checks)
**¿DNS del ISP caído? Cambio automático de tier en 15 segundos:**
- ✅ **Monitoreo de salud en tiempo real** (ping cada 15s)
- ✅ **Cambio automático de tier** al detectar falla
- ✅ **Cooldown de 60 segundos** para prevenir flapping
- ✅ **7 tiers DNS**: Cloudflare → Google → Quad9 → OpenDNS → Adguard → CloudflareFamily → DHCP
- ✅ **Notificaciones de Windows** en eventos de failover
- ✅ **No más errores "servidor DNS no responde"**

### 🔔 Sistema de Alertas Inteligente (NUEVO v2.1)
**Monitoreo proactivo de red:**
- ✅ **Umbrales configurables** (latencia, pérdida de paquetes, velocidad)
- ✅ **Alertas en tiempo real** vía notificaciones toast de Windows
- ✅ **Auto-resolución** cuando métricas vuelven a la normalidad
- ✅ **Historial de alertas** y estadísticas
- ✅ **Períodos de cooldown** para prevenir spam de notificaciones
- ✅ **6 tipos de alerta**: Latencia, Pérdida de Paquetes, Velocidad, DNS, Errores de Adaptador, Memoria

### 💾 Backups de Configuración (NUEVO v2.1)
**Nunca pierdas tu configuración de red:**
- ✅ **Snapshots de un click** de configuración DNS, IP, TCP y Registry
- ✅ **Restauración instantánea** a cualquier estado previo
- ✅ **Limpieza automática** (mantiene los últimos 50 backups)
- ✅ **Export/import JSON** para compartir configuraciones
- ✅ **Pre-backup antes de optimizaciones** (seguridad primero)

### 📊 Monitoreo Avanzado (NUEVO v2.1)
**Analíticas de red de grado profesional:**
- ✅ **4 gráficas en tiempo real** (Descarga, Subida, Latencia, Pérdida de Paquetes)
- ✅ **Zoom temporal** (5min, 15min, 30min, 1h, 6h, 24h, 7 días)
- ✅ **Integración con Matplotlib** con tema oscuro
- ✅ **Almacenamiento inteligente de datos** (estrategia 3-2-1: 24h todo, 7d por hora, 30d diario)
- ✅ **Historial de speed tests** con limpieza automática

### 🎨 Interfaz Moderna (NUEVO v2.1)
**Interfaz hermosa y funcional:**
- ✅ **Toggle Dark/Light theme**
- ✅ **Widgets modernos CustomTkinter**
- ✅ **Actualizaciones en tiempo real** sin bloquear UI
- ✅ **12 tabs de navegación** (Dashboard, Optimizaciones, DNS, Gráficas, Alertas, Backups, Configuración...)
- ✅ **Notificaciones toast de Windows** para todos los eventos

### 🎮 Casos de Uso del Mundo Real

**Gamers:**
- Juega FPS competitivo mientras Steam descarga en segundo plano
- Ping estable de 15-25ms incluso con familia viendo Netflix
- No más rubber-banding por pérdida de paquetes

**Trabajadores Remotos:**
- Llamadas Zoom/Teams cristalinas durante uploads de archivos
- Conexiones VPN permanecen estables
- Múltiples dispositivos no te ralentizarán

**Creadores de Contenido:**
- Sube a YouTube mientras navegas
- Live stream sin lag
- Transferencias de archivos grandes no matan otras apps

**Power Users:**
- Maximiza tu conexión Gigabit/fibra
- Optimizaciones TCP de nivel servidor
- Monitoreo y benchmarking de red

### 💡 Por Qué Funciona (Técnico)

**El Problema**: Windows usa **CUBIC** (algoritmo de 2006):
- ❌ **Reactivo**: Espera pérdida de paquetes para detectar congestión
- ❌ **Alta latencia**: Llena buffers de red (bufferbloat)
- ❌ **Entra en pánico fácilmente**: Pérdida de un paquete → 50% desaceleración
- ❌ **Desactualizado**: Diseñado para redes 2006, no WiFi 6/fibra moderno

**La Solución**: Linux usa **BBR** (algoritmo 2016 de Google):
- ✅ **Proactivo**: Detecta congestión vía RTT (antes de pérdida de paquetes)
- ✅ **Baja latencia**: Evita llenar buffers
- ✅ **Tolerante a pérdida**: Ignora pérdidas individuales de paquetes
- ✅ **Moderno**: Optimizado para redes de alta velocidad y alta latencia

**Enfoque de NetBoozt**: Como Windows no puede usar BBR directamente, optimizamos el entorno:
- 🔧 **HyStart++**: Inicio rápido tipo BBR
- 🔧 **PRR**: Recuperación suave de pérdidas
- 🔧 **ECN**: Señales de congestión del router (sin necesidad de pérdida de paquetes)
- 🔧 **TCP Pacing**: Envío suave de paquetes (anti-bufferbloat)
- 🔧 **RTO Optimizado**: Recuperación más rápida de timeouts

**Resultado**: Rendimiento tipo BBR en Windows (15-30% mejor throughput, 77% menor latencia)

## ✨ Características

### 🔧 Optimizaciones Principales

| Característica | Descripción | Más Info |
|----------------|-------------|----------|
| **Control de Congestión TCP** | Algoritmo similar a BBR para mejor rendimiento | [📖 Detalles](docs/optimizations/tcp-congestion-control.md) |
| **Receive Side Scaling** | Procesamiento de paquetes multi-CPU | 📖 Detalles |
| **TCP Autotuning** | Tamaño de búfer dinámico hasta 16MB | 📖 Detalles |
| **HyStart++** | Algoritmo rápido de slow-start | 📖 Detalles |
| **TCP Fast Open** | Reduce latencia de conexión | 📖 Detalles |

### 🌐 Resiliencia de Red & Monitoreo

| Característica | Descripción | Beneficio |
|----------------|-------------|-----------|
| **DNS Auto-Failover** | Health checks + cambio automático de tier | ¿DNS del ISP caído? Cambia en 15s automáticamente |
| **Fallback DNS de 7 Tiers** | Cloudflare → Google → Quad9 → OpenDNS → Adguard → CF Family → DHCP | Internet siempre activo, independiente del ISP |
| **Monitoreo en Tiempo Real** | 4 gráficas avanzadas con zoom temporal | Detecta throttling del ISP, patrones de pérdida de paquetes |
| **Sistema de Alertas** | Umbrales configurables + notificaciones | Recibe notificación antes de que los problemas te afecten |
| **Backups de Configuración** | Snapshots de un click + restauración | Vuelve a cualquier estado previo instantáneamente |
| **Historial de Speed Tests** | Estrategia de almacenamiento inteligente 3-2-1 | Rastrea rendimiento a lo largo del tiempo eficientemente |
| **Dark/Light Theme** | Interfaz profesional con toggle de tema | Visualización cómoda día o noche |

[**📚 Ver las 15+ optimizaciones →**](docs/optimizations/)

## 📊 Cómo Funciona NetBoozt

### Comparación de Algoritmos

#### Windows Por Defecto (Similar a CUBIC) - Reactivo
```
Throughput
    ^
    |     /\        /\        /\
    |    /  \      /  \      /  \      ← Pérdida de paquetes causa
    |   /    \    /    \    /    \       desaceleración dramática
    |  /      \  /      \  /      \
    | /        \/        \/        \
    +--------------------------------> Tiempo
        Pérdida  Pérdida  Pérdida
    
Promedio: 450 Mbps | Latencia: 85ms (bufferbloat)
```

#### NetBoozt Optimizado (Similar a BBR) - Proactivo
```
Throughput
    ^
    |  ________________________
    | /                        \       ← Throughput estable
    |/                          \        Latencia baja mantenida
    +--------------------------------> Tiempo
       Rampeo rápido    Estable
    
Promedio: 520 Mbps (+15.5%) | Latencia: 19ms (-77.6%)
```

**Diferencia Clave**: 
- **CUBIC**: Espera pérdida de paquetes → llena buffers → alta latencia → entra en pánico y desacelera
- **Similar a BBR**: Monitorea RTT → detecta acumulación de cola → mantiene velocidad óptima → baja latencia

[**📖 Leer Comparación Técnica Completa →**](docs/es/bbr-vs-cubic.md)

### Arquitectura del Sistema

![Arquitectura](docs/diagrams/architecture.md)

### Flujo de Optimización

![Flujo](docs/diagrams/optimization-flow.md)

[**📐 Ver Diagramas Interactivos →**](docs/diagrams/)

## ⚡ Inicio Rápido

### Windows (Recomendado)

```powershell
# 1. Clonar repositorio
git clone https://github.com/louzt/NetBoozt_InternetUpgrade.git
cd NetBoozt_InternetUpgrade/windows

# 2. Crear entorno virtual (usa --copies si Avast/antivirus bloquea)
python -m venv venv --copies
.\venv\Scripts\Activate.ps1

# 3. Instalar dependencias (incluye matplotlib para gráficas)
pip install -r requirements.txt

# 4. Instalar opcional: winotify para notificaciones toast de Windows
pip install winotify

# 5. Ejecutar GUI (como Administrador - REQUERIDO)
python run.py
```

**Uso por Primera Vez:**
1. Click **"🔄 Refresh Estado"** para detectar optimizaciones actuales
2. Revisa optimizaciones sugeridas (pre-seleccionadas según tu sistema)
3. Click **"✅ Aplicar Optimizaciones"** (crea backup automáticamente)
4. Habilita **"Auto-Failover"** en tab DNS para cambio automático de tier
5. Configura **umbrales de Alertas** en tab Alertas
6. Crea tu primer **Backup** en tab Backups

**Todos los cambios son 100% reversibles** vía tab Backups o botón "Revertir Todo".

### Linux (Próximamente)

```bash
# 1. Clonar repositorio
git clone https://github.com/louzt/NetBoozt_InternetUpgrade.git
cd NetBoozt_InternetUpgrade

# 2. Configuración
python3 -m venv venv
source venv/bin/activate
pip install -r linux/requirements.txt

# 3. Ejecutar CLI
sudo python linux/netboozt.py --profile balanced
```

## 📖 Documentación

### 📚 Primeros Pasos
- [⚙️ Guía de Instalación](docs/INSTALL.md)
- [🆕 Novedades v2.1](docs/WHATS_NEW_V2.1.md)
- [📝 Registro de Cambios](docs/CHANGELOG.md) | [📝 Español](CHANGELOG.md)
- [❓ FAQ (Español)](docs/es/FAQ.md)
- [❓ FAQ (English)](docs/FAQ.md)

### 🔧 Optimizaciones
- [📋 Vista General de Optimizaciones](docs/optimizations/)
- [🎯 Control de Congestión TCP](docs/optimizations/tcp-congestion-control.md)
- [🆚 BBR vs CUBIC (Español)](docs/es/bbr-vs-cubic.md)
- [🆚 BBR vs CUBIC (English)](docs/optimizations/bbr-vs-cubic.md)
- [⚡ Receive Side Scaling](docs/optimizations/rss.md)
- [🔄 TCP Window Scaling](docs/optimizations/tcp-window-scaling.md)

### 🏗️ Documentación Técnica
- [📐 Diagramas de Arquitectura](docs/diagrams/)
- [🔌 Referencia de API](docs/API.md)
- [🧪 Guía de Pruebas](docs/TESTING.md)
- [📐 Diagramas de Arquitectura](docs/diagrams/)
- [🔌 Referencia de API](docs/API.md)
- [🧪 Guía de Testing](docs/TESTING.md)

## 🎯 Perfiles de Optimización

NetBoozt ofrece 3 perfiles preconfigurados:

| Perfil | Nivel de Riesgo | Mejora de Rendimiento | Mejor Para |
|--------|-----------------|----------------------|------------|
| 🟢 **Conservador** | Bajo | +5-10% | Servidores de producción, estabilidad crítica |
| 🟡 **Balanceado** | Medio | +15-20% | **Uso general (recomendado)** |
| 🔴 **Agresivo** | Alto | +20-30% | Gaming, descargas, pruebas |

### Detalles de Perfiles

#### 🟢 Conservador
- TCP Window Scaling: 64KB
- RSS: Activado (2 CPUs)
- ECN: Desactivado
- Fast Open: Desactivado

#### 🟡 Balanceado (Recomendado)
- TCP Window Scaling: 256KB
- RSS: Activado (4 CPUs)
- ECN: Activado
- Fast Open: Activado
- HyStart++: Activado

#### 🔴 Agresivo
- TCP Window Scaling: 16MB
- RSS: Activado (Todas las CPUs)
- ECN: Activado
- Fast Open: Activado
- Todas las optimizaciones: Máximo

## 🧪 Integración Speedtest

NetBoozt incluye pruebas de velocidad integradas para benchmarking de optimizaciones:

```powershell
# Instalar speedtest-cli
pip install speedtest-cli

# Ejecutar desde GUI
# Click botón "Run Speed Test" antes y después de las optimizaciones
```

### Resultados de Ejemplo

**Antes de Optimización:**
```
Download: 450.23 Mbps
Upload: 120.45 Mbps
Ping: 28 ms
```

**Después de Optimización (Perfil Balanceado):**
```
Download: 520.18 Mbps (+15.5%)
Upload: 138.22 Mbps (+14.7%)
Ping: 19 ms (-32%)
```

Los resultados se guardan con timestamps en `speedtest_results_<timestamp>.json`

## 🛡️ Características de Seguridad

### Backup Automático
Cada optimización crea un backup de la configuración actual en:
```
optimizations_backup_<timestamp>.json
```

### Rollback con Un Click
Click "Restore Defaults" en GUI para revertir todos los cambios.

### Detección de Admin
Previene ejecuciones accidentales sin privilegios de administrador.

### Verificación de Compatibilidad
Verifica versión de Windows y soporte del adaptador de red.

## ⚠️ Notas Importantes

### 🔐 Se Requiere Administrador
NetBoozt modifica el registro del sistema y configuraciones de red:
```powershell
# Click derecho PowerShell → "Ejecutar como Administrador"
```

### 🛡️ Excepción de Antivirus Requerida
Algunos antivirus (Avast, Windows Defender) pueden bloquear la creación de venv:

**Windows Defender:**
```
Configuración → Protección contra virus y amenazas → Exclusiones → Agregar carpeta
→ Seleccionar "L:\NetworkFailover\NetBoozt"
```

**Avast:**
```
Menú → Configuración → General → Excepciones → Agregar Excepción
→ Buscar carpeta del proyecto
```

### 🔄 Reinicio Recomendado
Para mejores resultados, reinicia después de aplicar optimizaciones:
```powershell
# Aplicar optimizaciones en GUI
# Luego reiniciar Windows
```

### 📋 Requisitos
- **Windows 10/11** (Build 19041+)
- **Python 3.10+** (3.13 recomendado)
- **Privilegios de administrador**
- **Adaptador de red** con soporte RSS (la mayoría de adaptadores modernos)

### ✅ 100% Reversible
Todos los cambios pueden revertirse:
1. Click "Restore Defaults" en GUI
2. O ejecutar: `python windows/run.py --reset`
3. O aplicar manualmente archivos JSON de backup

## 🤝 Contribuir

¡Damos la bienvenida a contribuciones! Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías.

### 🚀 Roadmap de Desarrollo

#### v1.1.0 (Próximo Lanzamiento)
- [ ] Módulo Linux con soporte BBR
- [ ] Modo de optimización híbrido WSL
- [ ] CLI para scripting/automatización
- [ ] Testing automatizado (suite pytest)
- [ ] CI/CD con GitHub Actions

#### v1.2.0
- [ ] Dashboard de monitoreo en tiempo real
- [ ] Optimizaciones por aplicación
- [ ] Análisis de tráfico de red
- [ ] Historial de rollback (stack de deshacer)
- [ ] Importar/exportar perfiles

#### v2.0.0 (Visión)
- [ ] Soporte macOS
- [ ] Dashboard basado en web
- [ ] Auto-ajuste con machine learning
- [ ] Perfiles de optimización en la nube
- [ ] API REST para gestión remota

### 🐛 Reportes de Bugs
[Reportar issues en GitHub →](https://github.com/louzt/NetBoozt_InternetUpgrade/issues)

### 💡 Solicitudes de Características
[Enviar ideas →](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)

## 🌟 Reconocimientos

NetBoozt está inspirado por:
- **Google BBR** - Algoritmo de control de congestión
- **Linux TCP stack** - Características avanzadas de red
- **Microsoft PowerShell** - Automatización de Windows
- **speedtest-cli** - Benchmarking de red

### 🙏 Agradecimientos Especiales
- Contribuidores de la comunidad
- Beta testers
- Mantenedores de open-source

## 📞 Soporte

- **Website**: [www.loust.pro](https://www.loust.pro)
- **GitHub Issues**: [Reportar bugs](https://github.com/louzt/NetBoozt_InternetUpgrade/issues)
- **Discussions**: [Hacer preguntas](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)
- **Email**: opensource@loust.pro

## 📜 Licencia

Licencia MIT - [LICENSE](LICENSE)

## 👥 Autor

**LOUST** - [www.loust.pro](https://www.loust.pro)

---

<div align="center">

**Hecho con ❤️ por [LOUST](https://www.loust.pro)**

*Mejora Tu Internet, Mejora Tu Vida*

</div>
