"""
NetBoozt - DNS Health Checker
Monitoreo continuo de salud de servidores DNS

By LOUST (www.loust.pro)
"""

import subprocess
import threading
import time
import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from ..utils.logger import log_info, log_warning, log_error
except ImportError:
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")
    def log_error(msg): print(f"[ERROR] {msg}")


class DNSStatus(Enum):
    """Estado de salud de DNS"""
    UP = "up"           # < 50ms
    SLOW = "slow"       # 50-150ms
    DOWN = "down"       # > 150ms o timeout
    UNKNOWN = "unknown" # No testeado aún


@dataclass
class DNSHealth:
    """Estado de salud de un servidor DNS"""
    dns_server: str
    status: DNSStatus
    latency_ms: float
    packet_loss: float
    last_check: datetime
    consecutive_failures: int = 0


class DNSHealthChecker:
    """Monitorea salud de servidores DNS con ping continuo y resolución real"""
    
    # Thresholds - MÁS AGRESIVOS para mejor respuesta
    THRESHOLD_GOOD = 30      # ms - antes era 50
    THRESHOLD_SLOW = 80      # ms - antes era 150
    THRESHOLD_TIMEOUT = 2000 # ms (timeout) - antes era 3000
    MAX_CONSECUTIVE_FAILURES = 2  # antes era 3 - reacciona más rápido
    
    # Test domains para verificar resolución DNS real
    TEST_DOMAINS = ['google.com', 'microsoft.com', 'cloudflare.com']
    
    def __init__(self, check_interval: int = 10):  # Más frecuente: 10s vs 15s
        """
        Args:
            check_interval: Intervalo entre checks en segundos (default: 10)
        """
        self.check_interval = check_interval
        self.dns_servers: Dict[str, DNSHealth] = {}
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[str, DNSHealth], None]] = []
    
    def add_dns_server(self, dns_server: str):
        """Añadir servidor DNS a monitorear"""
        with self._lock:
            if dns_server not in self.dns_servers:
                self.dns_servers[dns_server] = DNSHealth(
                    dns_server=dns_server,
                    status=DNSStatus.UNKNOWN,
                    latency_ms=0.0,
                    packet_loss=0.0,
                    last_check=datetime.now(),
                    consecutive_failures=0
                )
                log_info(f"DNS server añadido para monitoreo: {dns_server}")
    
    def remove_dns_server(self, dns_server: str):
        """Remover servidor DNS del monitoreo"""
        with self._lock:
            if dns_server in self.dns_servers:
                del self.dns_servers[dns_server]
                log_info(f"DNS server removido: {dns_server}")
    
    def on_status_change(self, callback: Callable[[str, DNSHealth], None]):
        """Registrar callback para cambios de estado"""
        self._callbacks.append(callback)
    
    def start(self):
        """Iniciar monitoreo"""
        if self.is_running:
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True)
        self._thread.start()
        log_info("DNS Health Checker iniciado")
    
    def stop(self):
        """Detener monitoreo"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        log_info("DNS Health Checker detenido")
    
    def _check_loop(self):
        """Loop principal de checking"""
        while self.is_running:
            try:
                # Copiar lista de servidores para iterar
                with self._lock:
                    servers_to_check = list(self.dns_servers.keys())
                
                # Checkear cada servidor
                for dns_server in servers_to_check:
                    if not self.is_running:
                        break
                    
                    self._check_dns_server(dns_server)
                
                # Esperar antes del siguiente check
                time.sleep(self.check_interval)
                
            except Exception as e:
                log_error(f"Error en DNS check loop: {e}")
                time.sleep(5)  # Esperar un poco antes de reintentar
    
    def _check_dns_server(self, dns_server: str):
        """Checkear salud de un servidor DNS específico"""
        try:
            # Ping al DNS server
            latency, packet_loss = self._ping_server(dns_server)
            
            # Determinar estado
            if latency is None or latency >= self.THRESHOLD_TIMEOUT:
                new_status = DNSStatus.DOWN
            elif latency < self.THRESHOLD_GOOD:
                new_status = DNSStatus.UP
            elif latency < self.THRESHOLD_SLOW:
                new_status = DNSStatus.SLOW
            else:
                new_status = DNSStatus.DOWN
            
            # Actualizar estado
            with self._lock:
                if dns_server not in self.dns_servers:
                    return  # Fue removido
                
                old_health = self.dns_servers[dns_server]
                old_status = old_health.status
                
                # Contar fallas consecutivas
                if new_status == DNSStatus.DOWN:
                    consecutive_failures = old_health.consecutive_failures + 1
                else:
                    consecutive_failures = 0
                
                # Crear nuevo estado
                new_health = DNSHealth(
                    dns_server=dns_server,
                    status=new_status,
                    latency_ms=latency if latency is not None else 9999.0,
                    packet_loss=packet_loss,
                    last_check=datetime.now(),
                    consecutive_failures=consecutive_failures
                )
                
                self.dns_servers[dns_server] = new_health
                
                # Notificar si cambió el estado
                if old_status != new_status:
                    log_warning(f"DNS {dns_server}: {old_status.value} → {new_status.value} ({latency}ms)")
                    self._notify_callbacks(dns_server, new_health)
        
        except Exception as e:
            log_error(f"Error checkeando DNS {dns_server}: {e}")
    
    def _ping_server(self, server: str, count: int = 3) -> tuple[Optional[float], float]:
        """
        Ping a servidor y retornar latencia promedio y packet loss
        
        Returns:
            (latency_ms, packet_loss_percent)
        """
        try:
            # Windows ping command
            cmd = ["ping", "-n", str(count), "-w", "1000", server]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            output = result.stdout
            
            # Parsear latency (tiempo promedio)
            # Español: "Media = XXms" o "Promedio = XXms"
            # Inglés: "Average = XXms"
            latency_match = re.search(r"(?:Media|Promedio|Average)\s*=\s*(\d+)ms", output, re.IGNORECASE)
            
            if latency_match:
                latency = float(latency_match.group(1))
            else:
                # Si no hay match, asumir timeout
                return None, 100.0
            
            # Parsear packet loss
            # Español: "Perdidos = X (Y% perdidos)"
            # Inglés: "Lost = X (Y% loss)"
            loss_match = re.search(r"\((\d+)%\s*(?:perdidos|loss)\)", output, re.IGNORECASE)
            
            if loss_match:
                packet_loss = float(loss_match.group(1))
            else:
                packet_loss = 0.0
            
            return latency, packet_loss
            
        except subprocess.TimeoutExpired:
            log_warning(f"Ping timeout: {server}")
            return None, 100.0
        except Exception as e:
            log_error(f"Ping error: {e}")
            return None, 100.0
    
    def _notify_callbacks(self, dns_server: str, health: DNSHealth):
        """Notificar callbacks de cambio de estado"""
        for callback in self._callbacks:
            try:
                callback(dns_server, health)
            except Exception as e:
                log_error(f"Error en callback: {e}")
    
    def get_status(self, dns_server: str) -> Optional[DNSHealth]:
        """Obtener estado actual de un servidor DNS"""
        with self._lock:
            return self.dns_servers.get(dns_server)
    
    def get_all_status(self) -> Dict[str, DNSHealth]:
        """Obtener estado de todos los servidores"""
        with self._lock:
            return dict(self.dns_servers)
    
    def is_dns_healthy(self, dns_server: str) -> bool:
        """Verificar si DNS está saludable (UP o SLOW, no DOWN)"""
        status = self.get_status(dns_server)
        if not status:
            return False
        
        return status.status in (DNSStatus.UP, DNSStatus.SLOW) and \
               status.consecutive_failures < self.MAX_CONSECUTIVE_FAILURES
    
    def verify_dns_resolution(self, dns_server: str, domain: str = None) -> tuple[bool, float]:
        """
        Verificar resolución DNS real (no solo ping)
        
        Args:
            dns_server: Servidor DNS a probar
            domain: Dominio a resolver (default: google.com)
        
        Returns:
            (success, latency_ms)
        """
        domain = domain or self.TEST_DOMAINS[0]
        
        try:
            import time as t
            start = t.time()
            
            cmd = f"nslookup {domain} {dns_server}"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            elapsed = (t.time() - start) * 1000
            
            # Verificar que realmente resolvió
            if result.returncode == 0 and 'Address' in result.stdout:
                return True, elapsed
            
            return False, elapsed
            
        except subprocess.TimeoutExpired:
            return False, 3000.0
        except Exception as e:
            log_error(f"Error en verificación DNS {dns_server}: {e}")
            return False, 0.0
    
    def get_fastest_dns(self) -> Optional[str]:
        """Obtener el DNS más rápido actualmente"""
        with self._lock:
            healthy = [(dns, health) for dns, health in self.dns_servers.items() 
                      if health.status in (DNSStatus.UP, DNSStatus.SLOW)]
            
            if not healthy:
                return None
            
            # Ordenar por latencia
            healthy.sort(key=lambda x: x[1].latency_ms)
            return healthy[0][0]
    
    def benchmark_all_dns(self) -> Dict[str, Dict]:
        """
        Hacer benchmark completo de todos los DNS configurados
        
        Returns:
            {dns: {ping_ms, resolve_ms, status}}
        """
        results = {}
        
        with self._lock:
            servers = list(self.dns_servers.keys())
        
        for dns in servers:
            # Ping
            ping_latency, loss = self._ping_server(dns, count=3)
            
            # Resolución real
            resolve_ok, resolve_latency = self.verify_dns_resolution(dns)
            
            results[dns] = {
                'ping_ms': ping_latency,
                'packet_loss': loss,
                'resolve_ok': resolve_ok,
                'resolve_ms': resolve_latency,
                'status': 'OK' if resolve_ok and ping_latency and ping_latency < self.THRESHOLD_SLOW else 'SLOW/DOWN'
            }
        
        return results


if __name__ == "__main__":
    # Test
    checker = DNSHealthChecker(check_interval=10)
    
    # Callback de ejemplo
    def on_change(dns, health):
        print(f"🔔 {dns}: {health.status.value} ({health.latency_ms}ms)")
    
    checker.on_status_change(on_change)
    
    # Añadir DNS servers
    checker.add_dns_server("8.8.8.8")      # Google
    checker.add_dns_server("1.1.1.1")      # Cloudflare
    checker.add_dns_server("208.67.222.222") # OpenDNS
    
    # Iniciar
    checker.start()
    
    try:
        # Monitorear por 60 segundos
        for i in range(6):
            time.sleep(10)
            status_all = checker.get_all_status()
            print(f"\n--- Check {i+1} ---")
            for dns, health in status_all.items():
                print(f"{dns}: {health.status.value} ({health.latency_ms}ms, {health.packet_loss}% loss)")
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    finally:
        checker.stop()
