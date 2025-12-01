# NetBoozt v2.2 - Network Intelligence Update 🚀

> **By LOUST** (www.loust.pro)  
> **Release Date:** December 2025

---

## 📋 Quick Summary

| Category | What's New |
|----------|------------|
| **DNS Intelligence** | Parallel analysis with automatic selection |
| **System Tray** | Icon next to clock with quick actions |
| **Diagnostics** | 4-phase intelligent network diagnosis |
| **Windows Integration** | Real-time Event Log monitoring |
| **DNS** | Faster failover, real resolution testing, ISP DNS support |
| **CLI** | 4 new network tools |
| **Performance** | 50% faster failure detection |
| **Project Structure** | New `platforms/` organization for multi-platform |

---

## 🆕 New Features

### 1. DNS Intelligence (`dns_intelligence.py`) ⭐ NEW

**Intelligent DNS selection with parallel analysis:**

```
🧠 DNS Intelligence Features:
├── Parallel checks (4 concurrent workers)
├── Historical data analysis (24h retention)
├── Automatic score calculation
├── Real-time ranking updates
└── Auto-select best DNS
```

**Score Calculation:**
- **40%** Ping latency (lower is better)
- **30%** Resolve time (actual DNS resolution)
- **30%** Uptime percentage

**Key Capabilities:**
- Parallel DNS checking with ThreadPoolExecutor
- 5-minute interval between checks (configurable)
- Historical data for trend analysis
- Smart recommendations based on performance

**API:**
```python
from src.monitoring import DNSIntelligence, get_dns_intelligence

# Get instance
intel = get_dns_intelligence()

# Start monitoring (background thread)
intel.start_monitoring()

# Get current ranking
ranking = intel.get_ranking()
for rank, (server, metrics) in enumerate(ranking, 1):
    print(f"#{rank} {metrics.name}: {metrics.score:.0f} pts")

# Get best DNS automatically
best = intel.get_best_dns()
print(f"Recommended: {best.name} ({best.server})")

# Manual parallel check
intel.check_all_parallel()
```

**GUI Integration:**
- New `DNSIntelligenceTab` with visual cards
- Real-time updates as data arrives
- One-click DNS selection
- Performance summary

---

### 2. System Tray Icon (`system_tray.py`) ⭐ NEW

**Application icon next to the clock:**

```
🔔 System Tray Features:
├── Status indicator (color-coded)
├── Quick DNS change submenu
├── Run diagnostics shortcut
├── Show/Hide main window
├── Minimize to tray on close
└── Notification support
```

**Context Menu:**
- **Show Window** - Restore main application
- **DNS** → Cloudflare, Google, Quad9, etc.
- **Optimizations** → Conservative, Balanced, Aggressive
- **Run Diagnostics** - Quick network check
- **Settings** - Open preferences
- **Quit** - Exit completely

**Status Colors:**
- 🟢 **Green** - Everything working
- 🟡 **Yellow** - Warning/degraded
- 🔴 **Red** - Error/failure

**Minimize to Tray:**
- Closing window now minimizes to tray
- Notification: "NetBoozt sigue ejecutándose en segundo plano"
- Keeps monitoring active

**API:**
```python
from src.gui import SystemTrayIcon, get_system_tray

tray = SystemTrayIcon(
    on_show=show_window,
    on_quit=quit_app,
    on_diagnostics=run_diagnostics,
    on_settings=open_settings
)
tray.run()  # Blocks - run in thread

# Update status
tray.set_status("warning", "DNS latency high")

# Show notification
tray.show_notification("Title", "Message")
```

---

### 3. Windows Event Log Integration (`windows_events.py`)

**Real-time monitoring of Windows network events:**

```
📊 Event Types Monitored:
├── DNS-Client: Timeouts, failures
├── WLAN-AutoConfig: WiFi disconnects, limited connectivity
├── NCSI: Network status changes
├── DHCP-Client: IP assignment issues
└── Tcpip: TCP/IP stack events
```

**Key Capabilities:**
- Automatic classification of network events
- Historical event analysis (configurable lookback)
- Real-time callbacks for new events
- Summary statistics (events per hour, by type)

**Use Cases:**
- Detect DNS timeout patterns
- Track WiFi stability issues
- Correlate app issues with system events
- Identify recurring connectivity problems

**API:**
```python
from src.monitoring import WindowsEventMonitor, get_event_monitor

# Get instance
monitor = get_event_monitor()

# Callback for new events
def on_event(event):
    print(f"{event.event_type}: {event.message}")

monitor.on_event(on_event)
monitor.start()

# Get summary
summary = monitor.get_summary()
print(f"DNS timeouts in 5min: {summary['dns_timeouts_5min']}")
```

---

### 4. Intelligent Network Diagnostics (`network_diagnostics.py`)

**4-Phase Connection Chain Analysis:**

```
[Phase 1] ADAPTER    → Driver/hardware check
     ↓
[Phase 2] ROUTER     → Gateway connectivity (ping)
     ↓
[Phase 3] ISP        → External connectivity test
     ↓
[Phase 4] DNS        → Name resolution verification
```

**Output Example:**
```
============================================================
NETBOOZT - NETWORK DIAGNOSTIC REPORT
============================================================

Status: GOOD
Failure Point: none

--- Connection Chain ---
[1] Adapter (Wi-Fi): ✓ OK
[2] Router (Gateway): ✓ OK (5ms)
[3] ISP/Internet: ✓ OK (45ms)
[4] DNS: ✓ OK (50ms)

--- Recommendation ---
Your connection is working correctly.
============================================================
```

**Health Levels:**

| Status | Latency | Description |
|--------|---------|-------------|
| EXCELLENT | < 20ms | Optimal connection |
| GOOD | < 50ms | Normal operation |
| FAIR | < 100ms | Acceptable |
| POOR | < 200ms | May experience issues |
| BAD | ≥ 200ms | Degraded performance |
| DOWN | N/A | No connectivity |

**Detectable Failure Points:**

| Point | Typical Cause | Recommendation |
|-------|---------------|----------------|
| `ADAPTER` | Damaged driver, hardware | Restart adapter, update drivers |
| `ROUTER` | Disconnected cable, WiFi out of range | Check physical connection |
| `ISP` | Provider issue | Contact ISP |
| `DNS` | DNS server down or slow | Change DNS server |

**API:**
```python
from src.monitoring import NetworkDiagnostics, get_diagnostics

diag = get_diagnostics()

# Full diagnostic
result = diag.run_full_diagnostic()
print(f"Failure point: {result.failure_point}")
print(f"Recommendation: {result.recommendation}")

# Quick check
is_ok, message = diag.quick_check()
```

---

### 5. Enhanced DNS Health System (`dns_health.py`)

**Improved Thresholds (More Aggressive):**

| Setting | v2.1 | v2.2 | Impact |
|---------|------|------|--------|
| Good threshold | 50ms | **30ms** | Faster quality detection |
| Slow threshold | 150ms | **80ms** | Earlier warnings |
| Timeout | 3000ms | **2000ms** | Quicker failure detection |
| Max failures | 3 | **2** | Faster failover trigger |
| Check interval | 15s | **10s** | More responsive |

**New Capabilities:**

1. **`verify_dns_resolution()`** - Tests actual DNS resolution, not just ping
2. **`get_fastest_dns()`** - Returns best performing DNS server
3. **`benchmark_all_dns()`** - Full performance comparison

**Real Resolution Test:**
```python
checker = DNSHealthChecker()
checker.add_dns_server("1.1.1.1")
checker.add_dns_server("8.8.8.8")

# Verify real resolution (not just ping)
success, latency = checker.verify_dns_resolution("1.1.1.1", "google.com")

# Full benchmark
results = checker.benchmark_all_dns()
for dns, metrics in results.items():
    print(f"{dns}: ping={metrics['ping_ms']}ms, resolve={metrics['resolve_ms']}ms")
```

---

### 6. Faster Auto-Failover (`auto_failover.py`)

**Performance Improvements:**

| Setting | v2.1 | v2.2 | Benefit |
|---------|------|------|---------|
| Cooldown | 60s | **30s** | Can switch more frequently |
| Check interval | 15s | **10s** | Detects issues faster |
| Failures to switch | 3 | **2** | Reacts sooner |

**DNS Tier Hierarchy (8 Levels):**

```
Tier 1: Cloudflare     (1.1.1.1)       ← Fastest
Tier 2: Google         (8.8.8.8)       ← Most reliable
Tier 3: Quad9          (9.9.9.9)       ← Security focused
Tier 4: OpenDNS        (208.67.222.222)
Tier 5: AdGuard        (94.140.14.14)  ← Ad blocking
Tier 6: CleanBrowsing  (185.228.168.9)
Tier 7: Router/DHCP    (Auto)          ← ISP DNS fallback
Tier 8: ISP Detected   (Auto-detect)   ← Provider's detected DNS
```

**Automatic ISP DNS Detection:**
- Automatically detects your provider's DNS (Comcast, AT&T, etc.)
- Uses it as last resort if all public DNS fail
- Shows ISP info in diagnostics

---

### 7. Enhanced CLI (`netboozt_cli.py`)

**New Network Tools Menu:**

```
--- Network Tools ---
d › Diagnose      Full network diagnostic (4-phase)
n › DNS Test      Benchmark all DNS servers
w › Win Events    Show Windows network events
f › Fix DNS       Apply optimal DNS settings
```

#### Option `d` - Full Diagnostic

Runs complete 4-phase analysis:
- Identifies exact failure point
- Measures latency at each hop
- Provides specific recommendations

#### Option `n` - DNS Benchmark

- Tests Cloudflare, Google, Quad9, OpenDNS, AdGuard
- Measures ping latency and resolution time
- Recommends fastest server for your location

#### Option `w` - Windows Events

- Shows recent DNS timeouts
- WiFi disconnection history
- Counts issues per hour
- Alerts if many events detected

#### Option `f` - Fix DNS

- One-click DNS change
- Supports: Cloudflare, Google, Quad9, OpenDNS
- Auto-flushes DNS cache
- Reset to DHCP option

---

## � Executables

### Two Executables, One Project

| Executable | Description | Console | Use Case |
|------------|-------------|---------|----------|
| **NetBoozt_GUI.exe** | Graphical interface with system tray | Hidden | Regular users |
| **NetBoozt_CLI.exe** | Interactive command-line menu | Visible | Advanced users, servers |

### Build Both

```powershell
# Build both executables
.\scripts\build_nuitka.ps1

# Build only GUI
.\scripts\build_nuitka.ps1 -Target GUI

# Build only CLI
.\scripts\build_nuitka.ps1 -Target CLI
```

### Output Location

```
dist/
├── NetBoozt_GUI.exe    # ~25-30 MB - Graphical with tray icon
└── NetBoozt_CLI.exe    # ~20-25 MB - Command-line only
```

---

## 🔧 Technical Improvements

### Module Architecture

```
src/monitoring/
├── __init__.py            # Updated exports
├── adapter_manager.py     # Network adapter management
├── alert_system.py        # Alert system
├── auto_failover.py       # IMPROVED - Faster failover
├── dns_health.py          # IMPROVED - Real resolution testing
├── dns_intelligence.py    # NEW - Parallel DNS analysis ⭐
├── network_diagnostics.py # NEW - 4-phase diagnostics
├── realtime_monitor.py    # Real-time metrics
└── windows_events.py      # NEW - Windows Event Log

src/gui/
├── __init__.py            # Updated exports
├── modern_window.py       # Main window
├── dashboard.py           # Real-time metrics panel
├── system_tray.py         # NEW - Tray icon ⭐
├── dns_intelligence_tab.py # NEW - DNS ranking UI ⭐
└── ...
```

### New Exports in `__init__.py`

```python
# DNS Intelligence
from .dns_intelligence import (
    DNSIntelligence,
    DNSMetrics,
    get_dns_intelligence
)

# Windows events
from .windows_events import (
    WindowsEventMonitor,
    WindowsNetworkEvent, 
    NetworkEventType,
    get_event_monitor
)

# Network diagnostics
from .network_diagnostics import (
    NetworkDiagnostics,
    DiagnosticResult,
    FailurePoint,
    NetworkHealth,
    get_diagnostics
)
```

---

## 📊 Performance Comparison

### Before vs After (Failure Detection)

| Scenario | v2.1 | v2.2 | Improvement |
|----------|------|------|-------------|
| DNS timeout detection | 45s | 20s | **56% faster** |
| Failover execution | 75s | 40s | **47% faster** |
| Issue identification | Manual | Automatic | **100% automated** |
| Windows event correlation | None | Real-time | **New capability** |

---

## 🎯 Recommended Configuration

### Optimal DNS Setup by Region

**Mexico/Latin America:**
```
Primary:   1.1.1.1   (Cloudflare)
Secondary: 1.0.0.1   (Cloudflare backup)
Fallback:  Router DHCP (ISP DNS)
```

**USA/Canada:**
```
Primary:   1.1.1.1   (Cloudflare)
Secondary: 8.8.8.8   (Google)
Fallback:  Router DHCP (ISP DNS)
```

**Europe:**
```
Primary:   1.1.1.1   (Cloudflare)
Secondary: 9.9.9.9   (Quad9)
Fallback:  Router DHCP (ISP DNS)
```

---

## 🐛 Issues Fixed

- DNS health checker now tests actual resolution, not just ICMP ping
- Faster reaction to DNS failures (2 failures vs 3)
- Better handling of WiFi reconnection events
- Improved Spanish/English locale support in ping parsing
- Fixed encoding in adapter names with special characters

---

## 📝 Migration Notes

### For Existing Users

1. **No breaking changes** - All existing configurations work
2. **Automatic improvements** - Faster detection starts immediately
3. **New CLI options** - Available after update

### For Developers

New imports available:
```python
from src.monitoring import (
    # Windows Event Log
    WindowsEventMonitor,
    get_event_monitor,
    
    # Network Diagnostics
    NetworkDiagnostics,
    get_diagnostics,
    FailurePoint,
    NetworkHealth,
)
```

---

## 🔜 Coming Soon (v2.3)

- [ ] Historical performance graphs
- [ ] Network quality scoring over time
- [ ] Automatic DNS optimization based on location
- [ ] More system tray customization options
- [ ] Tauri/Rust version (v3.0 preparation)

---

## 📁 New Project Structure

```
NetBoozt/
├── platforms/                  # Multi-platform code
│   ├── python/                 # Current Python implementation
│   │   ├── src/
│   │   │   ├── gui/
│   │   │   │   ├── dns_intelligence_tab.py  # NEW
│   │   │   │   └── system_tray.py           # NEW
│   │   │   └── monitoring/
│   │   │       └── dns_intelligence.py      # NEW
│   │   ├── run_modern.py       # Updated with tray support
│   │   └── requirements.txt    # Updated with pystray
│   │
│   └── tauri/                  # Future Rust/Tauri (v3.0)
│       ├── src-tauri/          # Rust backend
│       └── src/                # Svelte frontend
│
├── shared/                     # Cross-platform configs
│   ├── dns_servers.json        # DNS definitions
│   └── optimizations.json      # TCP optimizations
│
└── scripts/                    # Build scripts
    ├── build_nuitka.ps1        # Recommended (25-35MB)
    ├── build_python.ps1        # PyInstaller
    └── dev.ps1                 # Development mode
```

---

## 🙏 Acknowledgments

NetBoozt v2.2 has been made possible thanks to:
- **Microsoft Windows Event Log** - System event integration
- **CustomTkinter** - Modern GUI framework
- **User community** - Feedback on DNS issues

---

<div align="center">

**Made with ❤️ by [LOUST](https://www.loust.pro)**

[🐛 Report Bug](https://github.com/louzt/NetBoozt_InternetUpgrade/issues) • [💡 Suggest Feature](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)

</div>
