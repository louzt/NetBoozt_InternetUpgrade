"""
NetBoozt - Script de Testing Rápido
Verifica que todos los módulos funcionan correctamente
"""

import sys
from pathlib import Path

# Colores para consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, details=""):
    """Imprimir resultado de test"""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"  {status} {name}")
    if details and not passed:
        print(f"    {Colors.YELLOW}└─ {details}{Colors.END}")

def test_imports():
    """Test 1: Verificar imports"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test 1: Verificación de Imports{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # Test CustomTkinter
    try:
        import customtkinter as ctk
        version = ctk.__version__ if hasattr(ctk, '__version__') else "unknown"
        print_test(f"CustomTkinter ({version})", True)
    except ImportError as e:
        print_test("CustomTkinter", False, str(e))
        return False
    
    # Test Matplotlib
    try:
        import matplotlib
        print_test(f"Matplotlib ({matplotlib.__version__})", True)
    except ImportError as e:
        print_test("Matplotlib", False, str(e))
        return False
    
    # Test TinyDB
    try:
        import tinydb
        print_test(f"TinyDB ({tinydb.__version__})", True)
    except ImportError as e:
        print_test("TinyDB", False, str(e))
        return False
    
    # Test psutil
    try:
        import psutil
        print_test(f"psutil ({psutil.__version__})", True)
    except ImportError as e:
        print_test("psutil", False, str(e))
        return False
    
    # Test PIL
    try:
        from PIL import Image
        print_test("Pillow (PIL)", True)
    except ImportError as e:
        print_test("Pillow", False, str(e))
        return False
    
    return True

def test_modules():
    """Test 2: Verificar módulos de NetBoozt"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test 2: Módulos de NetBoozt{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # Test Storage
    try:
        from src.storage import NetBooztStorage
        storage = NetBooztStorage()
        stats = storage.get_db_stats()
        total = stats['total_tests'] + stats['total_optimizations'] + stats['total_settings'] + stats['total_metrics']
        print_test(f"Storage Module (DB: {total} registros)", True)
    except Exception as e:
        print_test("Storage Module", False, str(e))
        return False
    
    # Test Monitoring
    try:
        from src.monitoring import NetworkMonitor, NetworkSnapshot
        print_test("Monitoring Module", True)
    except Exception as e:
        print_test("Monitoring Module", False, str(e))
        return False
    
    # Test Optimizations
    try:
        from src.optimizations import OptimizationDetector
        print_test("Optimizations Module", True)
    except Exception as e:
        print_test("Optimizations Module", False, str(e))
        return False
    
    # Test Dashboard
    try:
        from src.gui import NetworkDashboard
        print_test("Dashboard Module", True)
    except Exception as e:
        print_test("Dashboard Module", False, str(e))
        return False
    
    # Test GUI Principal
    try:
        from src.gui import ModernNetBoozt
        print_test("GUI Module (ModernNetBoozt)", True)
    except Exception as e:
        print_test("GUI Module", False, str(e))
        return False
    
    return True

def test_assets():
    """Test 3: Verificar assets (logos)"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test 3: Assets y Recursos{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    assets_dir = Path(__file__).parent / "assets"
    
    # Test logo
    logo_path = assets_dir / "loust_logo.png"
    if logo_path.exists():
        size_kb = logo_path.stat().st_size / 1024
        print_test(f"LOUST Logo ({size_kb:.1f} KB)", True)
    else:
        print_test("LOUST Logo", False, "Archivo no encontrado")
        return False
    
    # Test icon
    icon_path = assets_dir / "loust_icon.ico"
    if icon_path.exists():
        size_bytes = icon_path.stat().st_size
        print_test(f"LOUST Icon ({size_bytes} bytes)", True)
    else:
        print_test("LOUST Icon", False, "Archivo no encontrado")
        return False
    
    return True

def test_detection():
    """Test 4: Detección de optimizaciones"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test 4: Detección de Optimizaciones{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    try:
        from src.optimizations import OptimizationDetector
        detector = OptimizationDetector()
        
        # Detectar optimizaciones
        states = detector.detect_all()
        summary = detector.get_summary()
        
        print_test(
            f"Detección de Optimizaciones ({summary['enabled']}/{summary['total']} activas)",
            True
        )
        
        # Mostrar estado de algunas optimizaciones clave
        key_opts = ['tcp_congestion', 'rss', 'ecn', 'window_scaling']
        print(f"\n  {Colors.BLUE}Estado de optimizaciones clave:{Colors.END}")
        for opt_id in key_opts:
            if opt_id in states:
                state = states[opt_id]
                status = "✅ Activa" if state.enabled else "❌ Inactiva"
                print(f"    • {state.name}: {status}")
        
        return True
        
    except Exception as e:
        print_test("Detección de Optimizaciones", False, str(e))
        return False

def test_network_monitor():
    """Test 5: Monitor de red"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test 5: Monitor de Red{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    try:
        from src.monitoring import NetworkMonitor
        import time
        
        # Crear monitor
        monitor = NetworkMonitor("Ethernet", interval=0.5)
        monitor.start()
        
        print(f"  {Colors.BLUE}Iniciando monitor...{Colors.END}")
        time.sleep(2)  # Esperar 2 segundos
        
        # Verificar que hay datos
        snapshot = monitor.get_current_snapshot()
        
        if snapshot:
            print_test(
                f"Monitor de Red (Adaptador: {snapshot.adapter})",
                True
            )
            print(f"\n  {Colors.BLUE}Snapshot actual:{Colors.END}")
            print(f"    • Descarga: {snapshot.download_rate_mbps:.2f} Mbps")
            print(f"    • Subida: {snapshot.upload_rate_mbps:.2f} Mbps")
            print(f"    • Paquetes enviados: {snapshot.packets_sent}")
            print(f"    • Paquetes recibidos: {snapshot.packets_recv}")
        else:
            print_test("Monitor de Red", False, "No se capturó snapshot")
            monitor.stop()
            return False
        
        # Detener monitor
        monitor.stop()
        return True
        
    except Exception as e:
        print_test("Monitor de Red", False, str(e))
        return False

def test_storage():
    """Test 6: Storage (TinyDB)"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Test 6: Storage (TinyDB){Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    try:
        from src.storage import NetBooztStorage
        
        storage = NetBooztStorage()
        
        # Test: Guardar network test
        test_data = {
            'adapter': 'Ethernet',
            'download_mbps': 150.5,
            'upload_mbps': 50.2,
            'latency_ms': 15,
            'jitter_ms': 2,
            'packet_loss': 0.1,
            'mtu': 1500,
            'dns_servers': ['1.1.1.1', '8.8.8.8']
        }
        storage.save_network_test(test_data)
        print_test("Guardar Network Test", True)
        
        # Test: Obtener tests recientes
        recent = storage.get_recent_tests(limit=1)
        if recent:
            print_test(f"Recuperar Tests ({len(recent)} encontrados)", True)
        else:
            print_test("Recuperar Tests", False, "No se encontraron tests")
            return False
        
        # Test: Guardar métrica
        metric_data = {
            'adapter': 'Ethernet',
            'bytes_sent': 1000000,
            'bytes_recv': 5000000,
            'packets_sent': 1000,
            'packets_recv': 5000,
            'errors_in': 0,
            'errors_out': 0,
            'drops_in': 0,
            'drops_out': 0
        }
        storage.save_metric(metric_data)
        print_test("Guardar Métrica", True)
        
        # Test: Estadísticas de DB
        stats = storage.get_db_stats()
        total = stats['total_tests'] + stats['total_optimizations'] + stats['total_settings'] + stats['total_metrics']
        print(f"\n  {Colors.BLUE}Estadísticas de DB:{Colors.END}")
        print(f"    • Total registros: {total}")
        print(f"    • Network tests: {stats['total_tests']}")
        print(f"    • Optimizaciones: {stats['total_optimizations']}")
        print(f"    • Métricas: {stats['total_metrics']}")
        print(f"    • Tamaño DB: {stats['db_size_bytes']} bytes")
        
        return True
        
    except Exception as e:
        print_test("Storage", False, str(e))
        return False

def main():
    """Ejecutar todos los tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          NetBoozt v2.0 - Suite de Testing                 ║")
    print("║                  by LOUST (www.loust.pro)                  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    results = []
    
    # Ejecutar tests
    results.append(("Imports", test_imports()))
    results.append(("Módulos", test_modules()))
    results.append(("Assets", test_assets()))
    results.append(("Detección", test_detection()))
    results.append(("Monitor", test_network_monitor()))
    results.append(("Storage", test_storage()))
    
    # Resumen final
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Resumen de Tests{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✅{Colors.END}" if result else f"{Colors.RED}❌{Colors.END}"
        print(f"  {status} {name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests pasados{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡TODOS LOS TESTS PASARON!{Colors.END}")
        print(f"{Colors.GREEN}NetBoozt está listo para compilar a .exe{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️ ALGUNOS TESTS FALLARON{Colors.END}")
        print(f"{Colors.YELLOW}Revisa los errores antes de compilar{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
