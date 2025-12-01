#!/usr/bin/env python3
"""
NetBoozt - Project Structure Validator
Verifica que la estructura del proyecto esté completa y correcta.

Uso:
    python verify_structure.py
"""

import sys
from pathlib import Path

# Colores ANSI
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def check(condition, message):
    """Verificar condición y mostrar resultado."""
    if condition:
        print(f"  {GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"  {RED}✗{RESET} {message}")
        return False

def main():
    # Detectar raíz del proyecto
    script_dir = Path(__file__).parent.resolve()
    
    # Puede estar en platforms/python o en la raíz
    if script_dir.name == "python" and script_dir.parent.name == "platforms":
        project_root = script_dir.parent.parent
    else:
        project_root = script_dir
    
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{CYAN}  NetBoozt Project Structure Validator{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    print(f"Project root: {project_root}\n")
    
    all_ok = True
    
    # 1. Verificar estructura de directorios
    print(f"{YELLOW}[1/5] Checking directory structure...{RESET}")
    
    required_dirs = [
        "platforms/python/src",
        "platforms/python/src/gui",
        "platforms/python/src/monitoring",
        "platforms/python/src/optimizations",
        "platforms/python/src/storage",
        "platforms/python/src/utils",
        "platforms/python/assets",
        "platforms/tauri/src-tauri/src",
        "releases/windows",
        "shared",
        "docs",
        "scripts",
    ]
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        all_ok &= check(full_path.exists(), f"{dir_path}/")
    
    # 2. Verificar archivos principales
    print(f"\n{YELLOW}[2/5] Checking main files...{RESET}")
    
    required_files = [
        ("platforms/python/run_modern.py", "GUI launcher"),
        ("platforms/python/netboozt_cli.py", "CLI application"),
        ("platforms/python/NetBoozt_GUI.py", "GUI entry point"),
        ("platforms/python/requirements.txt", "Python dependencies"),
        ("platforms/python/README.md", "Python platform docs"),
        ("shared/dns_servers.json", "DNS configuration"),
        ("shared/optimizations.json", "TCP optimizations"),
        ("scripts/build_nuitka.ps1", "Nuitka build script"),
        ("scripts/build_python.ps1", "PyInstaller build script"),
        ("scripts/dev.ps1", "Development script"),
    ]
    
    for file_path, description in required_files:
        full_path = project_root / file_path
        all_ok &= check(full_path.exists(), f"{file_path} ({description})")
    
    # 3. Verificar módulos de monitoring
    print(f"\n{YELLOW}[3/5] Checking monitoring modules...{RESET}")
    
    monitoring_modules = [
        ("adapter_manager.py", "Network adapter management"),
        ("realtime_monitor.py", "Real-time metrics"),
        ("dns_health.py", "DNS health checker"),
        ("dns_intelligence.py", "DNS Intelligence (NEW)"),
        ("auto_failover.py", "Auto-failover system"),
        ("alert_system.py", "Alert system"),
        ("windows_events.py", "Windows Event Log"),
        ("network_diagnostics.py", "4-phase diagnostics"),
        ("__init__.py", "Module exports"),
    ]
    
    monitoring_dir = project_root / "platforms/python/src/monitoring"
    for module, description in monitoring_modules:
        full_path = monitoring_dir / module
        all_ok &= check(full_path.exists(), f"monitoring/{module} ({description})")
    
    # 4. Verificar módulos de GUI
    print(f"\n{YELLOW}[4/5] Checking GUI modules...{RESET}")
    
    gui_modules = [
        ("modern_window.py", "Main window"),
        ("dashboard.py", "Dashboard panel"),
        ("system_tray.py", "System tray icon (NEW)"),
        ("dns_intelligence_tab.py", "DNS Intelligence tab (NEW)"),
        ("splash_screen.py", "Splash screen"),
        ("theme_manager.py", "Theme management"),
        ("about_tab.py", "About tab"),
        ("__init__.py", "Module exports"),
    ]
    
    gui_dir = project_root / "platforms/python/src/gui"
    for module, description in gui_modules:
        full_path = gui_dir / module
        all_ok &= check(full_path.exists(), f"gui/{module} ({description})")
    
    # 5. Verificar Tauri structure
    print(f"\n{YELLOW}[5/5] Checking Tauri structure (v3.0 prep)...{RESET}")
    
    tauri_files = [
        ("platforms/tauri/src-tauri/Cargo.toml", "Rust dependencies"),
        ("platforms/tauri/src-tauri/tauri.conf.json", "Tauri config"),
        ("platforms/tauri/src-tauri/src/main.rs", "Rust entry point"),
        ("platforms/tauri/package.json", "Node dependencies"),
    ]
    
    for file_path, description in tauri_files:
        full_path = project_root / file_path
        all_ok &= check(full_path.exists(), f"{file_path} ({description})")
    
    # Resumen
    print(f"\n{CYAN}{'='*60}{RESET}")
    if all_ok:
        print(f"{GREEN}  ✓ All checks passed! Project structure is complete.{RESET}")
    else:
        print(f"{RED}  ✗ Some checks failed. Review the issues above.{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")
    
    # Info adicional
    print(f"{CYAN}Executables to build:{RESET}")
    print(f"  📦 NetBoozt_GUI.exe - Graphical interface with system tray")
    print(f"  📦 NetBoozt_CLI.exe - Command-line interface")
    print()
    print(f"{CYAN}Build command:{RESET}")
    print(f"  .\\scripts\\build_nuitka.ps1")
    print()
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
