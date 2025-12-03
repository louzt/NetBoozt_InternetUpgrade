# 🚀 NetBoozt - Sistema de Mejora de Internet

<div align="center">

![NetBoozt Logo](docs/assets/logo/netboozt_icon.png)

**Transforma tu Velocidad de Internet Sin Cambiar de ISP**

[![Tauri](https://img.shields.io/badge/Tauri-v3.0.0_Producción-00d4aa.svg?logo=tauri)](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v3.0.0)
[![Python Legacy](https://img.shields.io/badge/Python-v2.2.0_Legacy-gray.svg?logo=python)](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v2.2.0)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)
[![Plataforma](https://img.shields.io/badge/plataforma-Windows-0078D6.svg?logo=windows)]()
[![Stars](https://img.shields.io/github/stars/louzt/NetBoozt_InternetUpgrade?style=social)](https://github.com/louzt/NetBoozt_InternetUpgrade)

**Rendimiento BBR • Auto-Failover DNS • Monitoreo Real • Diagnóstico 4 Fases**

[English](README.md) | **Español**

[📦 Descargar](#-descargar) • [✨ Características](#-características) • [📖 Docs](#-documentación)

---

</div>

## 📦 Descargar

### 🦀 Versión Tauri (v3.0.0) — RECOMENDADA

Producción, moderna y ligera (~8MB) con **Rust + SvelteKit**. UI Glassmorphism.

| Plataforma | Descarga | Tech |
|------------|----------|------|
| Windows x64 | [NetBoozt_3.0.0.msi](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v3.0.0) | Rust + Tauri 1.5 |

### 🐍 Versión Python (v2.2.0) — Legacy

Implementación original (~25MB) con **Python + CustomTkinter**. Inicio lento, UI legacy.

| Plataforma | Descarga | Tech |
|------------|----------|------|
| Windows x64 | [NetBoozt_v2.2.0.exe](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v2.2.0) | Python 3.11 + Nuitka |

### ¿Cuál Elegir?

| | Tauri v3.0 | Python v2.2 |
|--|------------|-------------|
| **Estado** | 🟢 Producción | ⚪ Legacy |
| **Tamaño** | ~8 MB | ~25 MB |
| **Inicio** | <1s | ~5-8s |
| **UI** | Glass Moderno | CustomTkinter |
| **Rendimiento** | Optimizado | Más lento |
| **Recomendado** | ✅ Sí | Solo para CLI |

---

> *"Tenía fibra de 1 Gbps pero solo conseguía 450 Mbps. Mi ISP dijo 'es tu computadora.' Tenían razón—pero no como pensaban."*  
> **— David Mireles ([@lou404x](https://twitter.com/lou404x)), Creador**

**Por [LOUST](https://www.loust.pro)** | [opensource@loust.pro](mailto:opensource@loust.pro) | [@lou404x](https://twitter.com/lou404x)

---

## ✨ Características

| Categoría | Características |
|-----------|-----------------|
| **🚀 TCP/IP** | HyStart++, PRR, ECN, TCP Fast Open, Pacing, RSS, RSC, Autotuning |
| **🌐 DNS** | 8-Tier Auto-Failover, Health Checks reales, Detección ISP, Flush |
| **📊 Monitoreo** | Métricas tiempo real, 4 gráficas, Zoom temporal, Speed test |
| **🔔 Alertas** | 6 tipos, Umbrales config., Toast Windows, Auto-resolución |
| **💾 Backups** | Snapshots 1-click, Restauración, Export JSON, Auto-cleanup |
| **🔧 Diagnóstico** | 4-Fases, Windows Event Log, Detección throttling |

### Jerarquía DNS (8 Tiers)

| Tier | Proveedor | IP | Característica |
|------|-----------|-----|----------------|
| 1 | Cloudflare | 1.1.1.1 | Más rápido |
| 2 | Google | 8.8.8.8 | Más confiable |
| 3 | Quad9 | 9.9.9.9 | Seguridad |
| 4 | OpenDNS | 208.67.222.222 | Estable |
| 5 | AdGuard | 94.140.14.14 | Ad-blocking |
| 6 | CleanBrowsing | 185.228.168.9 | Familia |
| 7 | Router/DHCP | Auto | ISP fallback |
| 8 | ISP Detected | Auto-detect | Proveedor |

### Diagnóstico 4-Fases

```
Fase 1: Adaptador → Fase 2: Router → Fase 3: ISP → Fase 4: DNS
```

---

## 📖 Documentación

| Doc | Enlace |
|-----|--------|
| Instalación | [docs/INSTALL.md](docs/INSTALL.md) |
| Novedades v2.2 | [docs/WHATS_NEW_V2.2.md](docs/WHATS_NEW_V2.2.md) |
| BBR vs CUBIC | [docs/es/bbr-vs-cubic.md](docs/es/bbr-vs-cubic.md) |
| Optimizaciones | [docs/optimizations/](docs/optimizations/) |
| FAQ | [docs/es/FAQ.md](docs/es/FAQ.md) |
| Notas de Release | [RELEASE_NOTES.md](RELEASE_NOTES.md) |

---

## ⚡ Inicio Rápido

### Desarrollo Tauri (v3.0)

```powershell
cd platforms/tauri
npm install
npm run tauri dev
```

### Desarrollo Python (v2.2)

```powershell
cd windows
python -m venv venv --copies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_modern.py  # Ejecutar como Administrador
```

### Primer Uso
1. **Refresh Estado** → Detectar optimizaciones actuales
2. **Aplicar Perfil** → Conservador/Balanceado/Agresivo
3. **Activar DNS Auto-Failover** → Conectividad siempre activa
4. **Crear Backup** → Seguridad primero

---

## 🎯 Perfiles

| Perfil | Riesgo | Mejora | Ideal Para |
|--------|--------|--------|------------|
| 🟢 **Conservador** | Bajo | +5-10% | Producción |
| 🟡 **Balanceado** | Medio | +15-20% | General |
| 🔴 **Agresivo** | Alto | +20-30% | Gaming |

---

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) | [Reportar Bugs](https://github.com/louzt/NetBoozt_InternetUpgrade/issues)

---

## 📜 Licencia

MIT - [LICENSE](LICENSE)

---

<div align="center">

**Hecho con ❤️ por [LOUST](https://www.loust.pro)**

[Website](https://www.loust.pro) • [GitHub](https://github.com/louzt/NetBoozt_InternetUpgrade) • [Twitter](https://twitter.com/lou404x)

</div>
