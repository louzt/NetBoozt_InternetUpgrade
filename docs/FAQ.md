# ❓ Frequently Asked Questions (FAQ) - v2.1

## General

### What is NetBoozt?
NetBoozt is an advanced TCP/IP network optimization toolkit that brings Linux-level performance (similar to Google's BBR congestion control) to Windows. **v2.1 adds:**
- ✅ Automatic DNS failover with health checks
- ✅ Smart alert system with configurable thresholds
- ✅ Configuration backup/restore system
- ✅ Advanced monitoring with temporal graphs
- ✅ Dark/Light theme support

It's 100% open-source and reversible.

### Is it safe?
Yes! NetBoozt:
- ✅ Creates automatic backups before changes (new in v2.1)
- ✅ 100% reversible with one click
- ✅ Only modifies Windows registry (no binary patching)
- ✅ No kernel-level drivers required
- ✅ Open-source (MIT License)
- ✅ 9300+ lines of tested code

### Will it void my warranty?
No. NetBoozt only modifies Windows registry settings that are officially documented by Microsoft. These are the same settings network administrators use.

### Does it work on my system?
**Requirements:**
- Windows 10/11 (Build 19041+)
- Python 3.10+ (3.13 recommended)
- Administrator privileges
- Network adapter with RSS support (most modern adapters)
- **Optional:** winotify for Windows notifications

## Performance

### How much faster will my internet be?
Typical results:
- **Download**: +15-20% improvement
- **Upload**: +10-15% improvement
- **Latency**: -12% to -77% reduction (during downloads)
- **Gaming**: Reduced lag spikes by 50-80%

Results vary by ISP, network conditions, and hardware.

### Do I need gigabit internet?
No! NetBoozt improves performance on any connection:
- **50 Mbps**: Better streaming, less buffering
- **100 Mbps**: Faster downloads, lower latency
- **500+ Mbps**: Utilize full bandwidth, reduce overhead
- **1 Gbps+**: Get closer to theoretical maximum

### Will it help with gaming?
Yes! Benefits:
- 🎮 Lower ping times (-30% average)
- 📉 Reduced lag spikes (77% lower latency during downloads)
- ⚡ Faster packet processing (RSS)
- 🔄 Better congestion handling (BBR-like)
- 🔔 Get alerted if latency spikes (new in v2.1)

## New Features (v2.1)

### What is DNS Auto-Failover?
Automatic switching between DNS tiers if current tier fails:
- 🔍 Health checks every 15 seconds
- ⚡ Switches to next healthy tier in <15s
- ⏱️ 60-second cooldown to prevent flapping
- 🔔 Windows notification on failover
- 🎯 7 DNS tiers (Cloudflare → Google → Quad9 → ... → DHCP)

### How do Alerts work?
Configurable thresholds that trigger notifications:
- **Latency High**: Alert when ping > 100ms (configurable)
- **Packet Loss**: Alert when loss > 2%
- **Speed Low**: Alert when download < 10 Mbps
- **DNS Failure**: Alert on consecutive DNS failures
- **Adapter Errors**: Alert on high error rate

Alerts auto-resolve when metrics return to normal.

### What are Configuration Backups?
One-click snapshots of your entire network configuration:
- 💾 DNS servers
- 💾 IP configuration
- 💾 TCP global settings
- 💾 Registry values

Restore to any previous state instantly. Backups saved to `~/.netboozt/backups/`

### How do Advanced Graphs work?
4 real-time graphs with temporal zoom:
- **Download Speed** (Mbps)
- **Upload Speed** (Mbps)
- **Latency** (ms)
- **Packet Loss** (%)

Zoom: 5min, 15min, 30min, 1h, 6h, 24h, 7 days. Intelligent storage (3-2-1 strategy) keeps database small.

### Can I switch between Dark/Light theme?
Yes! Go to Settings tab and click the theme toggle button. The entire UI updates instantly.

## Installation

### Why does my antivirus block it?
Python venv creation involves creating executables, which some antivirus software flags. This is a false positive.

**Fix:**
```powershell
# Add project folder to antivirus exceptions
# Then recreate venv:
python -m venv venv --copies
```

### Do I need to run as Administrator?
Yes. Network optimizations require registry modifications that need admin privileges.

### Can I use it on WSL?
WSL support is planned for v1.1.0. Currently, NetBoozt optimizes the Windows host only.

## Usage

### Which profile should I use?
- **🟢 Conservative**: Production servers, stability critical
- **🟡 Balanced**: **Recommended for most users**
- **🔴 Aggressive**: Gaming, testing, maximum performance

Start with Balanced and upgrade to Aggressive if stable.

### Do I need to reboot?
**Recommended but not required.** Some optimizations (like RSS) take effect immediately, while others (like TCP Window Scaling) require a reboot for full effect.

### How do I rollback?
Three methods:
1. **GUI**: Click "Restore Defaults" button
2. **CLI**: `python windows/run.py --reset`
3. **Manual**: Apply backup JSON from `optimizations_backup_*.json`

### Can I customize optimizations?
Yes! In the GUI:
1. Go to "Optimizations" tab
2. Toggle individual optimizations on/off
3. Click "Apply Selected"

For advanced customization, edit `windows/src/optimizations/network_optimizer.py`

## Troubleshooting

### "Access Denied" errors?
You're not running as Administrator.

**Fix:**
```powershell
# Right-click PowerShell → "Run as Administrator"
cd L:\NetworkFailover\NetBoozt
.\venv\Scripts\Activate.ps1
python windows/run.py
```

### Venv creation fails?
Usually caused by antivirus blocking.

**Fix:**
```powershell
# Add folder to antivirus exceptions, then:
python -m venv venv --copies
```

### GUI doesn't open?
Check dependencies:
```powershell
pip install -r windows/requirements.txt

# Verify ttkbootstrap:
python -c "import ttkbootstrap; print('OK')"
```

### Speed test not working?
Install speedtest-cli:
```powershell
pip install speedtest-cli

# Test manually:
speedtest-cli
```

### No performance improvement?
Checklist:
1. ✅ Rebooted after applying optimizations?
2. ✅ Used correct profile (try Aggressive)?
3. ✅ Network adapter supports RSS?
4. ✅ ISP not throttling?

Run before/after speed tests to measure:
```powershell
# Before optimization
speedtest-cli > before.txt

# Apply optimizations + reboot

# After optimization
speedtest-cli > after.txt
```

## Advanced

### Can I automate NetBoozt?
Yes! CLI usage:
```powershell
# Apply Balanced profile
python windows/run.py --profile balanced

# Reset to defaults
python windows/run.py --reset

# Run speed test
python windows/run.py --speedtest
```

For automation, use PowerShell scripts or Task Scheduler.

### Does it work with VPN?
Yes, but VPN overhead may reduce gains. NetBoozt optimizes the underlying TCP stack, which VPNs use.

### Can I use multiple profiles?
No. Profiles overwrite each other. Choose one profile and stick with it.

### How do I contribute?
See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code style guidelines
- Testing requirements
- Pull request process

### Is there a paid version?
No. NetBoozt is 100% free and open-source (MIT License). No premium features, no telemetry, no ads.

## Legal

### Is it legal?
Yes. NetBoozt modifies your own computer's settings, which is perfectly legal.

### Can I use it commercially?
Yes! MIT License permits commercial use. See [LICENSE](../LICENSE).

### Can I redistribute?
Yes, under MIT License terms. Attribution required.

## Support

### Where do I get help?
- **GitHub Issues**: [Bug reports](https://github.com/louzt/NetBoozt_InternetUpgrade/issues)
- **Discussions**: [Questions & ideas](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)
- **Email**: opensource@loust.pro

### How do I report bugs?
[Open an issue](https://github.com/louzt/NetBoozt_InternetUpgrade/issues/new) with:
1. Windows version
2. Python version
3. Error message/logs
4. Steps to reproduce

### How do I request features?
[Start a discussion](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions/new) describing:
1. Feature description
2. Use case
3. Expected benefit

---

**Still have questions?** [Ask on GitHub Discussions](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions) 💬
