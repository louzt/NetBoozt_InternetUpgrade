# 🚀 NetBoozt - Internet Upgrade System

<div align="center">

![NetBoozt Logo](docs/assets/logo/netboozt_icon.png)

**Transform Your Internet Speed Without Changing Your ISP**

[![Tauri](https://img.shields.io/badge/Tauri-v3.0.0_Production-00d4aa.svg?logo=tauri)](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v3.0.0)
[![Python Legacy](https://img.shields.io/badge/Python-v2.2.0_Legacy-gray.svg?logo=python)](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v2.2.0)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6.svg?logo=windows)]()
[![Stars](https://img.shields.io/github/stars/louzt/NetBoozt_InternetUpgrade?style=social)](https://github.com/louzt/NetBoozt_InternetUpgrade)

**BBR-like Performance • Auto DNS Failover • Real-time Monitoring • 4-Phase Diagnostics**

**English** | [Español](README.es.md)

[📦 Download](#-download) • [✨ Features](#-features) • [📖 Docs](#-documentation)

---

</div>

## 📦 Download

### 🦀 Tauri Version (v3.0.0-beta) — NEW!

Modern, lightweight (~8MB) with **Rust + SvelteKit**. Glassmorphism UI.

| Platform | Download | Tech |
|----------|----------|------|
| Windows x64 | [NetBoozt_3.0.0-beta.msi](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v3.0.0-beta.1) | Rust + Tauri 1.5 |

### 🐍 Python Version (v2.2.0) — Stable

Battle-tested (~25MB) with **Python + CustomTkinter**. Includes full CLI.

| Platform | Download | Tech |
|----------|----------|------|
| Windows x64 | [NetBoozt_v2.2.0.exe](https://github.com/louzt/NetBoozt_InternetUpgrade/releases/tag/v2.2.0) | Python 3.11 + Nuitka |

### Which Version?

| | Tauri v3.0 | Python v2.2 |
|--|------------|-------------|
| **Status** | 🟡 Beta | 🟢 Stable |
| **Size** | ~8 MB | ~25 MB |
| **Best For** | Early adopters | Production |
| **CLI** | ❌ | ✅ |

---

> *"I had 1 Gbps fiber but only got 450 Mbps. My ISP said 'it's your computer.' They were right—but not how they thought."*  
> **— David Mireles ([@lou404x](https://twitter.com/lou404x)), Creator**

**By [LOUST](https://www.loust.pro)** | [opensource@loust.pro](mailto:opensource@loust.pro) | [@lou404x](https://twitter.com/lou404x)

---

## ✨ Features

### 🚀 TCP/IP Optimization (BBR-like for Windows)

| Optimization | Description | Benefit |
|--------------|-------------|---------|
| **HyStart++** | Fast slow-start | +15-20% throughput |
| **PRR** | Proportional Rate Reduction | Smooth loss recovery |
| **ECN** | Congestion Notification | No packet loss needed |
| **TCP Fast Open** | Data in SYN | -1 RTT |
| **TCP Pacing** | Smooth sending | -77% latency |
| **RSS/RSC** | Multi-CPU processing | Less CPU overhead |

### 🌐 DNS Auto-Failover (8 Tiers)

ISP DNS down? Automatic switch in 15s:
- Tier 1-2: Cloudflare/Google (speed)
- Tier 3-5: Quad9/OpenDNS/AdGuard (security)
- Tier 6-8: CleanBrowsing/DHCP/ISP (fallback)

### 🔍 4-Phase Diagnostics

```
Adapter → Router → ISP → DNS
```

### 📊 Real-time Monitoring

- Live graphs (Download/Upload/Latency)
- Windows Event Log integration
- Configurable alerts

---

## 📖 Documentation

- [⚙️ Installation](docs/INSTALL.md)
- [🆕 What's New v2.2](docs/WHATS_NEW_V2.2.md)
- [❓ FAQ](docs/FAQ.md)
- [📋 Optimizations](docs/optimizations/)
- [🆚 BBR vs CUBIC](docs/optimizations/bbr-vs-cubic.md)

---

## 💻 Quick Start

### Tauri (Dev)
```bash
cd platforms/tauri && npm install && npm run tauri dev
```

### Python (Dev)
```powershell
cd windows
python -m venv venv && .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_modern.py  # Run as Administrator
```

---

## 🎯 Profiles

| Profile | Risk | Gain |
|---------|------|------|
| 🟢 Conservative | Low | +5-10% |
| 🟡 **Balanced** | Medium | +15-20% |
| 🔴 Aggressive | High | +20-30% |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs welcome!

---

## 📜 License

MIT License - [LICENSE](LICENSE)

---

<div align="center">

**Made with ❤️ by [LOUST](https://www.loust.pro)**

⭐ Star if it helped! ⭐

</div>
