# 🎉 What's New in NetBoozt v2.1

## 🚀 Major Features

### 1. DNS Auto-Failover System 🔄

**Automatic DNS tier switching with health monitoring**

- ✅ **Real-time health checks** every 15 seconds
- ✅ **Automatic failover** when current tier fails
- ✅ **60-second cooldown** to prevent flapping
- ✅ **7 DNS tiers** with intelligent fallback
- ✅ **Windows notifications** on failover events

**How it works:**
```
Cloudflare (1.1.1.1) ─┐
                      ├─► Health Checker (ping every 15s)
Google (8.8.8.8) ─────┤
                      │
Quad9 (9.9.9.9) ──────┤   Tier DOWN? ──► Auto-switch to next healthy tier
                      │
OpenDNS ──────────────┤
                      │
... 7 tiers total ────┘
```

**Benefits:**
- Never lose internet due to ISP DNS outages
- Faster DNS resolution (often faster than ISP DNS)
- Automatic recovery without manual intervention
- Visual indicators in GUI (🟢 UP / 🟡 SLOW / 🔴 DOWN)

**Usage:**
1. Go to **"Failover DNS"** tab
2. Enable **"Auto-Failover"** switch
3. System monitors automatically
4. Get notified when tier changes

---

### 2. Smart Alert System 🔔

**Proactive network monitoring with configurable thresholds**

- ✅ **6 alert types**: Latency, Packet Loss, Speed, DNS, Adapter, Memory
- ✅ **Configurable thresholds** per alert type
- ✅ **Auto-resolution** when metrics return to normal
- ✅ **Alert history** with statistics
- ✅ **Cooldown periods** to prevent notification spam
- ✅ **Windows toast notifications**

**Alert Types:**

| Alert | Default Threshold | Severity |
|-------|------------------|----------|
| Latency High | 100ms | Warning |
| Packet Loss High | 2% | Critical |
| Speed Low | 10 Mbps | Warning |
| DNS Failure | 3 consecutive fails | Critical |
| Adapter Errors | 10 errors/min | Warning |
| Memory High | 80% usage | Info |

**Example Alert Flow:**
```
Latency: 120ms (exceeds 100ms threshold)
    ↓
Alert triggered → Toast notification
    ↓
Latency drops to 50ms
    ↓
Alert auto-resolved
```

**Usage:**
1. Go to **"Alertas"** tab
2. Configure thresholds for each metric
3. Click **"Guardar Configuración"**
4. System monitors automatically
5. View active alerts and history

---

### 3. Configuration Backup System 💾

**One-click snapshots of network configuration**

- ✅ **Instant snapshots** of DNS, IP, TCP, Registry settings
- ✅ **One-click restore** to any previous state
- ✅ **Automatic cleanup** (keeps last 50 backups)
- ✅ **JSON export/import** for sharing configs
- ✅ **Pre-backup before optimizations** (safety first)

**What gets backed up:**
```json
{
  "backup_id": "20251110_164030",
  "timestamp": "2025-11-10T16:40:30",
  "adapter_name": "Ethernet",
  "dns_servers": ["1.1.1.1", "1.0.0.1"],
  "ip_config": {
    "IPAddress": "192.168.1.100",
    "PrefixLength": 24
  },
  "tcp_settings": {
    "AutoTuningLevelLocal": "Normal",
    "CongestionProvider": "CTCP",
    "EcnCapability": "Enabled"
  },
  "registry_values": {
    "NetworkThrottlingIndex": 4294967295,
    "Tcp1323Opts": 1
  }
}
```

**Benefits:**
- Rollback to any previous state instantly
- Experiment safely (always can restore)
- Share working configs with others
- Track configuration changes over time

**Usage:**
1. Go to **"Backups"** tab
2. Click **"📸 Crear Backup Ahora"**
3. To restore: Select backup → Click **"↩️ Restaurar"**
4. Backups stored in `~/.netboozt/backups/`

---

### 4. Advanced Monitoring Graphs 📊

**Professional-grade network analytics with temporal zoom**

- ✅ **4 real-time graphs**: Download, Upload, Latency, Packet Loss
- ✅ **Temporal zoom**: 5min, 15min, 30min, 1h, 6h, 24h, 7 days
- ✅ **Matplotlib integration** with dark theme
- ✅ **Automatic axis formatting** based on time range
- ✅ **Intelligent data storage** (3-2-1 strategy)

**The 4 Graphs:**

1. **Download Speed (Mbps)**
   - Color: Green (#00d4aa)
   - Tracks: Real-time download throughput
   - Useful for: Detecting ISP throttling, speed drops

2. **Upload Speed (Mbps)**
   - Color: Purple (#6c5ce7)
   - Tracks: Real-time upload throughput
   - Useful for: Video calls, live streaming, cloud backups

3. **Latency (ms)**
   - Color: Yellow (#fdcb6e)
   - Tracks: Network round-trip time
   - Useful for: Gaming, VoIP quality, responsiveness

4. **Packet Loss (%)**
   - Color: Red (#ff6b6b)
   - Tracks: Percentage of lost packets
   - Useful for: Network quality, stability issues

**Temporal Zoom:**
```
5 min    → Every 5s update (high resolution)
15 min   → Every 5s update
30 min   → Every 10s update
1 hour   → Minute markers
6 hours  → Hour markers (every 2h)
24 hours → Hour markers (every 2h)
7 days   → Day markers
```

**3-2-1 Storage Strategy:**
- **Last 24h**: Keep ALL data points
- **1-7 days**: Keep 1 sample per hour (averaged)
- **8-30 days**: Keep 1 sample per day
- **30+ days**: Keep 1 sample per week

Result: Comprehensive history without bloating database.

**Usage:**
1. Go to **"Gráficas"** tab
2. Select time range from dropdown
3. Graphs update automatically
4. Data stored indefinitely (auto-cleanup)

---

### 5. Dark/Light Theme System 🎨

**Professional UI with theme toggle**

- ✅ **Two complete themes**: Dark and Light
- ✅ **Instant switching** without restart
- ✅ **Consistent colors** across all tabs
- ✅ **CustomTkinter integration**
- ✅ **Preference saved** for next session

**Dark Theme (Default):**
```
Background: #0a0a0a (deep black)
Cards: #1a1a1a (dark gray)
Primary: #00d4aa (turquoise)
Text: #ffffff (white)
```

**Light Theme:**
```
Background: #ffffff (white)
Cards: #f5f5f5 (light gray)
Primary: #00b894 (green)
Text: #1a1a1a (dark)
```

**Usage:**
1. Go to **"Configuración"** tab
2. Click **🎨 Theme Toggle** button
3. UI updates instantly
4. Preference saved automatically

---

## 🔧 Technical Improvements

### Architecture Enhancements

**New Modules:**
```
src/
├── monitoring/
│   ├── alert_system.py       (NEW) - Smart alerts with thresholds
│   ├── auto_failover.py      (NEW) - DNS auto-failover logic
│   └── dns_health.py         (NEW) - Health checker with ping
├── storage/
│   ├── backup_system.py      (NEW) - Configuration snapshots
│   └── speed_test_storage.py (NEW) - Intelligent data storage
├── gui/
│   ├── advanced_graphs.py    (NEW) - Matplotlib graphs with zoom
│   └── theme_manager.py      (NEW) - Dark/Light theme system
└── utils/
    └── notifications.py      (NEW) - Windows toast notifications
```

**Code Statistics:**
- **9,300+ lines** of Python code
- **8 new modules** in v2.1
- **3 new GUI tabs** (Graphs, Alerts, Backups)
- **100+ new functions**

### Performance Optimizations

1. **Non-blocking UI**
   - All network operations in background threads
   - GUI remains responsive during optimizations
   - Real-time updates via callbacks

2. **Efficient Data Storage**
   - TinyDB for local caching (1-hour validity)
   - 3-2-1 strategy for speed test history
   - Automatic cleanup of old data

3. **Smart Caching**
   - Optimization state cached (1 hour)
   - Invalidation on apply
   - Fast startup (no PowerShell spam)

### Integration Improvements

**DNS Health Checker + Auto-Failover:**
```python
# Tight integration
DNSHealthChecker → monitors all DNS servers every 15s
        ↓
AutoFailoverManager → detects failures, switches tiers
        ↓
NotificationManager → shows Windows toast
        ↓
GUI → updates tier badges (🟢/🟡/🔴)
```

**Alert System + Monitoring:**
```python
# Real-time checking
NetworkMonitor → captures latency, speed, packet loss
        ↓
AlertSystem → compares against thresholds
        ↓
Alert triggered → notification + history
        ↓
Auto-resolve when metrics normalize
```

---

## 🐛 Bug Fixes

1. **Fixed:** Optimization detection now uses cache (no PowerShell spam on startup)
2. **Fixed:** Thread-safe dashboard updates (no UI freezing)
3. **Fixed:** Memory leaks in network monitor (proper cleanup)
4. **Fixed:** Bare except clauses replaced with specific exceptions
5. **Fixed:** Print statements replaced with proper logging
6. **Fixed:** Cleanup handlers for all background threads

---

## 📋 Migration Guide

### From v1.0 to v2.1

**No breaking changes!** v2.1 is fully backward compatible.

**New optional dependencies:**
```powershell
pip install winotify  # For Windows notifications
```

**Database migration:**
- TinyDB creates new tables automatically
- Old speedtest results remain intact
- New tables: `optimization_state_cache`, `alerts`, `backups`

**Configuration:**
- All v1.0 settings work in v2.1
- New features disabled by default (opt-in)
- Enable Auto-Failover manually in DNS tab
- Configure Alert thresholds in Alerts tab

---

## 🎯 What's Next?

### Planned for v2.2

- [ ] **Per-application optimizations** (optimize specific apps)
- [ ] **Network traffic analysis** (real-time packet inspection)
- [ ] **Rollback history** (undo stack for optimizations)
- [ ] **Profile import/export** (share configs as files)
- [ ] **Automated testing** (pytest suite)

### Planned for v3.0

- [ ] **Machine learning auto-tuning** (learn from your usage)
- [ ] **REST API** for remote management
- [ ] **Web dashboard** (browser-based UI)
- [ ] **macOS support**
- [ ] **Cloud optimization profiles**

---

## 🙏 Acknowledgments

Special thanks to:
- Community beta testers
- Contributors who reported bugs
- Users who suggested features

---

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/louzt/NetBoozt_InternetUpgrade/issues)
- **Discussions**: [Ask questions](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)
- **Email**: opensource@loust.pro
- **Twitter/X**: [@lou404x](https://twitter.com/lou404x)

---

<div align="center">

**Made with ❤️ by [LOUST](https://www.loust.pro)**

*NetBoozt v2.1 - More Power, More Control*

</div>
