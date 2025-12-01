# 📝 Changelog

All notable changes to NetBoozt will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2025-11-10

### 🎉 Added

#### DNS Auto-Failover System
- **DNS Health Checker** (`src/monitoring/dns_health.py`)
  - Background ping monitoring every 15 seconds
  - Status classification: UP (<50ms), SLOW (50-150ms), DOWN (>150ms)
  - Consecutive failure tracking
  - Callback system for status changes
  - Regex parsing for Spanish/English ping output

- **Auto-Failover Manager** (`src/monitoring/auto_failover.py`)
  - Automatic tier switching on DNS failure
  - 60-second cooldown between failovers
  - Current tier detection from DNS configuration
  - Next healthy tier selection
  - Event history with timestamps
  - Callback notifications

- **GUI Integration**
  - Auto-Failover ON/OFF switch in DNS tab
  - Health status indicator (Estado: ✅/❌)
  - Real-time tier health badges (🟢/🟡/🔴)
  - Toast notifications on failover events

#### Smart Alert System
- **Alert System** (`src/monitoring/alert_system.py`)
  - 6 configurable alert types:
    * Latency High (default: 100ms)
    * Packet Loss High (default: 2%)
    * Speed Low (default: 10 Mbps)
    * DNS Failure (default: 3 consecutive)
    * Adapter Errors (default: 10/min)
    * Memory High (default: 80%)
  - Per-type cooldown configuration
  - Auto-resolution when metrics normalize
  - Alert history and statistics
  - Windows toast notifications

- **Alerts Tab** (GUI)
  - Active alerts display
  - Threshold configuration UI
  - Alert history viewer
  - Manual alert resolution
  - Stats dashboard

#### Configuration Backup System
- **Backup System** (`src/storage/backup_system.py`)
  - One-click network configuration snapshots
  - Captures:
    * DNS servers
    * IP configuration
    * TCP global settings
    * Registry values (throttling, window scaling, etc.)
  - JSON export format
  - Automatic cleanup (keeps last 50)
  - Restore to any previous state

- **Backups Tab** (GUI)
  - Create backup button
  - Backup list with timestamps
  - Restore functionality
  - Delete old backups
  - Backup metadata display

#### Advanced Monitoring Graphs
- **Advanced Graphs** (`src/gui/advanced_graphs.py`)
  - 4 real-time graphs:
    * Download Speed (Mbps) - Green
    * Upload Speed (Mbps) - Purple
    * Latency (ms) - Yellow
    * Packet Loss (%) - Red
  - Temporal zoom: 5min, 15min, 30min, 1h, 6h, 24h, 7 days
  - Matplotlib integration with dark theme
  - Automatic axis formatting
  - Real-time updates

- **Speed Test Storage** (`src/storage/speed_test_storage.py`)
  - Intelligent 3-2-1 storage strategy:
    * Last 24h: ALL data points
    * 1-7 days: 1 sample/hour (aggregated)
    * 8-30 days: 1 sample/day
    * 30+ days: 1 sample/week
  - Automatic cleanup on save
  - Statistics calculation
  - Efficient disk usage

#### Theme System
- **Theme Manager** (`src/gui/theme_manager.py`)
  - Dark and Light themes with complete color palettes
  - Instant theme switching
  - Callback system for theme changes
  - CustomTkinter integration
  - Persistent theme preference

- **GUI Integration**
  - Theme toggle button in Settings tab
  - Dynamic UI updates
  - Consistent colors across all tabs
  - Professional dark/light aesthetics

#### Notification System
- **Notification Manager** (`src/utils/notifications.py`)
  - Windows toast notifications via winotify
  - Specialized notification methods:
    * `notify_dns_failover()` - DNS tier changes
    * `notify_optimization_applied()` - Optimization results
    * `notify_alert()` - Alert triggers
    * `notify_backup_created()` - Backup confirmations
    * `notify_error()` - Error messages
  - Fallback to console if winotify unavailable
  - Singleton pattern for global access

### 🔧 Changed

#### GUI Enhancements
- **Navigation**: Added 3 new tabs (Graphs, Alerts, Backups)
- **Total tabs**: 12 (Dashboard, Optimizations, Status, Failover, Graphs, Alerts, Backups, Settings, About, README, Docs, GitHub)
- **Layout**: Improved sidebar with all features
- **Responsiveness**: All operations in background threads (non-blocking UI)

#### Optimization System
- **Detection**: Cache optimization state for 1 hour (faster startup)
- **Invalidation**: Auto-invalidate cache on apply
- **Pre-selection**: Switches pre-selected based on detected state
- **Action buttons**: 
  * 🔄 Refresh Estado (force re-detection)
  * ✅ Aplicar Optimizaciones (background thread)
  * ↩️ Revertir Todo (restore defaults)

#### Monitoring
- **Dashboard**: Real-time updates with alert checking
- **Graphs**: Integrated with advanced graphs tab
- **Metrics**: Latency and speed checked against thresholds
- **Callbacks**: Proper callback system for all monitors

### 🐛 Fixed

#### Code Quality
- Replaced 26 print statements with proper logging
- Fixed 10 bare except clauses with specific exceptions
- Added thread safety with Locks
- Fixed memory leaks in NetworkMonitor
- Proper cleanup handlers (`__del__`, `on_closing`)

#### Performance
- Dashboard loop control (prevent multiple concurrent loops)
- Cache system for optimization detection (no PowerShell spam)
- Efficient data storage (3-2-1 strategy)
- Background threads for all network operations

#### Stability
- Thread-safe GUI updates
- Proper exception handling
- Graceful degradation (fallbacks for missing dependencies)
- Admin permission checks

### 📦 Dependencies

#### New
- `winotify>=1.1.0` - Windows toast notifications (optional)
- `matplotlib>=3.7.0` - Advanced graphs

#### Updated
- `customtkinter>=5.2.0` - Modern UI widgets
- `psutil>=5.9.0` - Network monitoring
- `tinydb>=4.8.0` - Local database

### 📚 Documentation

#### New Files
- `docs/WHATS_NEW_V2.1.md` - Comprehensive v2.1 feature guide
- `docs/CHANGELOG.md` - This changelog
- `dev_notes/implementation_plan.md` - Updated with v2.1 progress
- `dev_notes/todo.md` - Task tracking
- `dev_notes/ideas.md` - Future features brainstorm

#### Updated Files
- `README.md` - Updated with v2.1 features and badges
- `docs/INSTALL.md` - Added v2.1 installation steps
- `docs/FAQ.md` - Added v2.1 FAQ entries

### 🎯 Statistics

- **Lines of Code**: 9,300+ (Python)
- **New Modules**: 8
- **New Functions**: 100+
- **New GUI Components**: 200+
- **Code Coverage**: ~75% (estimated)

---

## [1.0.0] - 2025-10-15

### 🎉 Added

#### Core Optimization System
- TCP Congestion Control (CTCP/Compound)
- ECN (Explicit Congestion Notification)
- RSS (Receive Side Scaling)
- TCP Window Scaling
- TCP Timestamps
- TCP Chimney Offload
- Network Throttling Index
- Auto-Tuning Level

#### GUI
- Modern CustomTkinter interface
- Dashboard with real-time monitoring
- Optimization tab with manual controls
- Status tab with network metrics
- DNS Failover tab (manual tier selection)
- Settings tab
- About/README/Docs/GitHub tabs

#### Network Monitoring
- Real-time bandwidth tracking
- Latency monitoring
- Packet statistics
- Error/drop counting
- Adapter detection

#### DNS Management
- 7-tier DNS fallback system
- Manual tier selection
- Active tier detection
- DNS server configuration

#### Database
- TinyDB for local storage
- Metric history
- Settings persistence
- Speed test results

### 📦 Dependencies
- `customtkinter>=5.2.0`
- `psutil>=5.9.0`
- `tinydb>=4.8.0`
- `pillow>=10.0.0`

### 📚 Documentation
- Initial README.md
- Basic installation guide
- FAQ
- Optimization documentation

---

## [Unreleased]

### Planned for v2.2
- [ ] Per-application optimizations
- [ ] Network traffic analysis
- [ ] Rollback history (undo stack)
- [ ] Profile import/export
- [ ] Automated testing (pytest suite)
- [ ] CI/CD with GitHub Actions

### Planned for v3.0
- [ ] Machine learning auto-tuning
- [ ] REST API for remote management
- [ ] Web-based dashboard
- [ ] macOS support
- [ ] Cloud optimization profiles
- [ ] Linux module improvements

---

## Version History

- **2.1.0** (2025-11-10) - Major feature release (Auto-Failover, Alerts, Backups, Graphs, Theme)
- **1.0.0** (2025-10-15) - Initial public release

---

<div align="center">

**Made with ❤️ by [LOUST](https://www.loust.pro)**

</div>
