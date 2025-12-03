# NetBoozt Release Notes

## 🚀 v3.0.0 (Tauri) - December 2025 — PRODUCTION

**Release de producción de NetBoozt Tauri** - Versión moderna, rápida y ligera.

### ✨ Características

- **Dashboard en Tiempo Real**: Métricas de red con gráficas animadas
- **Diagnóstico de 4 Fases**: Adapter → Router → ISP → DNS
- **Speed Test Integrado**: Test de velocidad con API de Cloudflare
- **Sistema de Alertas**: Notificaciones configurables
- **DNS Auto-Failover**: Cambio automático entre 8 tiers de DNS
- **Optimizaciones TCP/IP**: Perfiles BBR-like para Windows
- **GitHub Integration**: Stats del repositorio en tiempo real
- **Dev Utilities**: cURL, Ping, Traceroute, Port Scanner, Header Checker

### 🎨 UI/UX

- Interfaz Glassmorphism moderna
- Tema oscuro con fondos degradados personalizables
- Colores de acento configurables
- Sidebar colapsable con indicadores de estado
- Floating Terminal integrado

### 🔧 Tecnologías

- **Frontend**: SvelteKit + TypeScript
- **Backend**: Rust + Tauri 1.5
- **Tamaño**: ~8MB instalador

### ⚡ Rendimiento vs Python Legacy

| Métrica | Tauri v3.0 | Python v2.2 |
|---------|------------|-------------|
| **Startup** | <1s | 5-8s |
| **Memoria RAM** | ~50MB | ~150MB |
| **Tamaño instalador** | ~8MB | ~25MB |
| **UI Response** | 60fps | ~15-30fps |
| **CPU idle** | <1% | 3-5% |

---

## 📦 v2.2.0 (Python) - December 2025 — LEGACY

**Versión legacy de NetBoozt Python** - Implementación original, mantenida para CLI.

### ✨ Características

- **15+ Optimizaciones TCP/IP**: RSS, RSC, ECN, HyStart++, PRR, TFO, Pacing
- **3 Perfiles**: Conservador, Balanceado, Agresivo
- **Monitoreo en Tiempo Real**: Métricas de red con gráficas
- **DNS Auto-Failover**: 8 tiers de DNS con health check real
- **Windows Event Log**: Monitoreo de eventos DNS, WLAN, NCSI
- **Diagnóstico Completo**: 4 fases de diagnóstico de red
- **CLI Interactivo**: Interfaz de línea de comandos completa

### 🎨 GUI

- CustomTkinter con tema oscuro
- 12+ tabs organizados
- Gráficas con matplotlib

### 📋 Requisitos

- Windows 10/11
- Python 3.11+ (para desarrollo)
- Permisos de administrador

### 📥 Instalación

1. Descarga `NetBoozt_v2.2.0_Windows.exe`
2. Ejecuta como administrador
3. ¡Listo!

---

## 📜 Changelog

### v2.2.0
- Nuevo: Windows Event Log monitoring
- Nuevo: Diagnóstico de 4 fases
- Nuevo: DNS ISP auto-detect
- Mejorado: Health check DNS con resolución real
- Mejorado: UI con mejor distribución visual
- Fix: Sincronización de estado de monitoreo

### v2.1.0
- Nuevo: Speed Test integrado
- Nuevo: Sistema de alertas
- Mejorado: Gráficas en tiempo real

### v2.0.0
- Reescritura completa con CustomTkinter
- Nueva arquitectura modular
- CLI interactivo

---

**Desarrollado por LOUST** | [www.loust.pro](https://loust.pro) | MIT License
