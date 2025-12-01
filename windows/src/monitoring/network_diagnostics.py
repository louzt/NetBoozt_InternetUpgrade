"""
NetBoozt - Network Issue Detector
Diagnóstico inteligente del punto de falla en la conexión

By LOUST (www.loust.pro)

Fases de diagnóstico:
1. Adaptador local (driver, hardware)
2. Router/Gateway (conexión LAN/WiFi)  
3. ISP (conectividad externa)
4. DNS (resolución de nombres)
5. Destino específico
"""

import subprocess
import threading
import time
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

try:
    from ..utils.logger import log_info, log_warning, log_error
except ImportError:
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")
    def log_error(msg): print(f"[ERROR] {msg}")


class FailurePoint(Enum):
    """Puntos de falla en la conexión"""
    NONE = "none"                    # Todo OK
    ADAPTER = "adapter"              # Problema con adaptador/driver
    ROUTER = "router"                # No llega al router
    ISP = "isp"                      # Router OK pero sin internet
    DNS = "dns"                      # Internet OK pero DNS falla
    DESTINATION = "destination"      # DNS OK pero destino específico falla
    UNKNOWN = "unknown"


class NetworkHealth(Enum):
    """Estado de salud de red"""
    EXCELLENT = "excellent"   # Latencia < 20ms
    GOOD = "good"             # Latencia < 50ms
    FAIR = "fair"             # Latencia < 100ms
    POOR = "poor"             # Latencia < 200ms
    BAD = "bad"               # Latencia >= 200ms o pérdida
    DOWN = "down"             # Sin conectividad


@dataclass
class DiagnosticResult:
    """Resultado de diagnóstico"""
    timestamp: datetime
    failure_point: FailurePoint
    health: NetworkHealth
    
    # Métricas por fase
    adapter_ok: bool
    router_latency_ms: Optional[float]
    router_ok: bool
    isp_latency_ms: Optional[float]
    isp_ok: bool
    dns_latency_ms: Optional[float]
    dns_ok: bool
    
    # Detalles
    adapter_name: str
    gateway_ip: str
    dns_servers: List[str]
    
    message: str
    recommendation: str


class NetworkDiagnostics:
    """Sistema de diagnóstico inteligente de red"""
    
    # IPs de prueba por fase
    TEST_TARGETS = {
        'cloudflare': '1.1.1.1',
        'google': '8.8.8.8',
        'quad9': '9.9.9.9',
        'level3': '4.2.2.2',
    }
    
    # Dominios para probar DNS
    TEST_DOMAINS = [
        'google.com',
        'microsoft.com',
        'cloudflare.com',
    ]
    
    def __init__(self):
        self.last_result: Optional[DiagnosticResult] = None
        self._lock = threading.Lock()
    
    def run_full_diagnostic(self, adapter_name: str = None) -> DiagnosticResult:
        """
        Ejecutar diagnóstico completo de red
        
        Returns:
            DiagnosticResult con punto de falla identificado
        """
        log_info("Iniciando diagnóstico completo de red...")
        
        # Fase 0: Obtener info del adaptador
        if not adapter_name:
            adapter_name, gateway_ip, dns_servers = self._get_adapter_info()
        else:
            _, gateway_ip, dns_servers = self._get_adapter_info(adapter_name)
        
        if not adapter_name:
            return self._create_result(
                FailurePoint.ADAPTER,
                NetworkHealth.DOWN,
                adapter_ok=False,
                adapter_name="",
                gateway_ip="",
                dns_servers=[],
                message="No se encontró adaptador de red activo",
                recommendation="Verifica que tu WiFi o Ethernet esté conectado"
            )
        
        # Fase 1: Verificar adaptador
        adapter_ok = self._check_adapter(adapter_name)
        if not adapter_ok:
            return self._create_result(
                FailurePoint.ADAPTER,
                NetworkHealth.DOWN,
                adapter_ok=False,
                adapter_name=adapter_name,
                gateway_ip=gateway_ip,
                dns_servers=dns_servers,
                message=f"Problema con adaptador {adapter_name}",
                recommendation="Reinicia el adaptador o actualiza drivers"
            )
        
        # Fase 2: Verificar router/gateway
        router_latency, router_ok = self._ping_target(gateway_ip, timeout=2)
        if not router_ok:
            return self._create_result(
                FailurePoint.ROUTER,
                NetworkHealth.DOWN,
                adapter_ok=True,
                router_latency_ms=router_latency,
                router_ok=False,
                adapter_name=adapter_name,
                gateway_ip=gateway_ip,
                dns_servers=dns_servers,
                message=f"No hay conexión con router ({gateway_ip})",
                recommendation="Verifica tu conexión WiFi o cable Ethernet. Reinicia el router si es necesario."
            )
        
        # Fase 3: Verificar ISP (ping a IPs externas)
        isp_latency, isp_ok = self._check_isp()
        if not isp_ok:
            return self._create_result(
                FailurePoint.ISP,
                NetworkHealth.DOWN,
                adapter_ok=True,
                router_latency_ms=router_latency,
                router_ok=True,
                isp_latency_ms=isp_latency,
                isp_ok=False,
                adapter_name=adapter_name,
                gateway_ip=gateway_ip,
                dns_servers=dns_servers,
                message="Router OK pero sin conexión a Internet",
                recommendation="El problema está en tu ISP o la configuración del router. Contacta a tu proveedor."
            )
        
        # Fase 4: Verificar DNS
        dns_latency, dns_ok = self._check_dns(dns_servers)
        if not dns_ok:
            return self._create_result(
                FailurePoint.DNS,
                NetworkHealth.POOR,
                adapter_ok=True,
                router_latency_ms=router_latency,
                router_ok=True,
                isp_latency_ms=isp_latency,
                isp_ok=True,
                dns_latency_ms=dns_latency,
                dns_ok=False,
                adapter_name=adapter_name,
                gateway_ip=gateway_ip,
                dns_servers=dns_servers,
                message=f"Internet OK pero DNS ({dns_servers[0] if dns_servers else 'N/A'}) no responde",
                recommendation="Cambia a DNS más rápido (Cloudflare 1.1.1.1 o Google 8.8.8.8)"
            )
        
        # Todo OK - calcular salud general
        health = self._calculate_health(router_latency, isp_latency, dns_latency)
        
        result = self._create_result(
            FailurePoint.NONE,
            health,
            adapter_ok=True,
            router_latency_ms=router_latency,
            router_ok=True,
            isp_latency_ms=isp_latency,
            isp_ok=True,
            dns_latency_ms=dns_latency,
            dns_ok=True,
            adapter_name=adapter_name,
            gateway_ip=gateway_ip,
            dns_servers=dns_servers,
            message=f"Conexión OK - {health.value.upper()}",
            recommendation=self._get_health_recommendation(health, router_latency, dns_latency)
        )
        
        with self._lock:
            self.last_result = result
        
        return result
    
    def quick_check(self) -> Tuple[bool, str]:
        """
        Verificación rápida de conectividad
        
        Returns:
            (is_connected, message)
        """
        # Ping rápido a múltiples destinos
        for name, ip in self.TEST_TARGETS.items():
            latency, ok = self._ping_target(ip, timeout=1, count=1)
            if ok:
                return True, f"Conectado ({name}: {latency:.0f}ms)"
        
        return False, "Sin conexión a Internet"
    
    def _get_adapter_info(self, adapter_name: str = None) -> Tuple[str, str, List[str]]:
        """Obtener información del adaptador activo"""
        try:
            cmd = """
            $adapter = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1
            if ($adapter) {
                $config = Get-NetIPConfiguration -InterfaceIndex $adapter.ifIndex
                $dns = (Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4).ServerAddresses
                
                @{
                    Name = $adapter.Name
                    Gateway = $config.IPv4DefaultGateway.NextHop
                    DNS = $dns
                } | ConvertTo-Json
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                
                dns_servers = data.get('DNS', [])
                if isinstance(dns_servers, str):
                    dns_servers = [dns_servers]
                
                return (
                    data.get('Name', ''),
                    data.get('Gateway', ''),
                    dns_servers
                )
                
        except Exception as e:
            log_error(f"Error obteniendo info de adaptador: {e}")
        
        return '', '', []
    
    def _check_adapter(self, adapter_name: str) -> bool:
        """Verificar estado del adaptador"""
        try:
            cmd = f"(Get-NetAdapter -Name '{adapter_name}').Status"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            return 'Up' in result.stdout
            
        except Exception:
            return False
    
    def _ping_target(self, target: str, timeout: int = 2, count: int = 2) -> Tuple[Optional[float], bool]:
        """
        Ping a un destino
        
        Returns:
            (latency_ms, success)
        """
        if not target:
            return None, False
            
        try:
            cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), target]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout * count + 2,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                # Parsear latencia
                match = re.search(r'(?:Media|Promedio|Average)\s*=\s*(\d+)ms', result.stdout, re.IGNORECASE)
                if match:
                    return float(match.group(1)), True
                
                # Si no hay promedio, buscar tiempo individual
                match = re.search(r'tiempo[=<](\d+)ms|time[=<](\d+)ms', result.stdout, re.IGNORECASE)
                if match:
                    return float(match.group(1) or match.group(2)), True
            
            return None, False
            
        except subprocess.TimeoutExpired:
            return None, False
        except Exception as e:
            log_error(f"Error en ping a {target}: {e}")
            return None, False
    
    def _check_isp(self) -> Tuple[Optional[float], bool]:
        """Verificar conectividad ISP pingando IPs externas"""
        latencies = []
        
        for name, ip in self.TEST_TARGETS.items():
            latency, ok = self._ping_target(ip, timeout=2, count=1)
            if ok and latency is not None:
                latencies.append(latency)
                if len(latencies) >= 2:  # Con 2 OK es suficiente
                    break
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            return avg_latency, True
        
        return None, False
    
    def _check_dns(self, dns_servers: List[str]) -> Tuple[Optional[float], bool]:
        """Verificar resolución DNS"""
        if not dns_servers:
            # Usar DNS públicos si no hay configurados
            dns_servers = ['8.8.8.8', '1.1.1.1']
        
        for domain in self.TEST_DOMAINS:
            for dns in dns_servers[:2]:  # Solo probar primeros 2
                try:
                    start = time.time()
                    cmd = f"nslookup {domain} {dns}"
                    
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=3,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    
                    elapsed = (time.time() - start) * 1000
                    
                    if result.returncode == 0 and 'Address' in result.stdout:
                        return elapsed, True
                        
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
        
        return None, False
    
    def _calculate_health(self, router_latency: float, isp_latency: float, 
                         dns_latency: float) -> NetworkHealth:
        """Calcular salud general de la conexión"""
        # Usar la métrica más relevante (ISP latency)
        primary = isp_latency if isp_latency else router_latency
        
        if primary is None:
            return NetworkHealth.DOWN
        elif primary < 20:
            return NetworkHealth.EXCELLENT
        elif primary < 50:
            return NetworkHealth.GOOD
        elif primary < 100:
            return NetworkHealth.FAIR
        elif primary < 200:
            return NetworkHealth.POOR
        else:
            return NetworkHealth.BAD
    
    def _get_health_recommendation(self, health: NetworkHealth, 
                                   router_latency: float, dns_latency: float) -> str:
        """Generar recomendación basada en métricas"""
        recommendations = []
        
        if health == NetworkHealth.EXCELLENT:
            return "Tu conexión está óptima. No se requieren cambios."
        
        if router_latency and router_latency > 10:
            recommendations.append("Considera acercarte al router o usar cable Ethernet")
        
        if dns_latency and dns_latency > 100:
            recommendations.append("Prueba cambiar a DNS más rápido (1.1.1.1)")
        
        if health in (NetworkHealth.POOR, NetworkHealth.BAD):
            recommendations.append("Verifica interferencias WiFi o congestión de red")
        
        return ". ".join(recommendations) if recommendations else "Monitorea la conexión para detectar patrones"
    
    def _create_result(self, failure_point: FailurePoint, health: NetworkHealth,
                       adapter_ok: bool = False,
                       router_latency_ms: float = None,
                       router_ok: bool = False,
                       isp_latency_ms: float = None,
                       isp_ok: bool = False,
                       dns_latency_ms: float = None,
                       dns_ok: bool = False,
                       adapter_name: str = "",
                       gateway_ip: str = "",
                       dns_servers: List[str] = None,
                       message: str = "",
                       recommendation: str = "") -> DiagnosticResult:
        """Crear resultado de diagnóstico"""
        return DiagnosticResult(
            timestamp=datetime.now(),
            failure_point=failure_point,
            health=health,
            adapter_ok=adapter_ok,
            router_latency_ms=router_latency_ms,
            router_ok=router_ok,
            isp_latency_ms=isp_latency_ms,
            isp_ok=isp_ok,
            dns_latency_ms=dns_latency_ms,
            dns_ok=dns_ok,
            adapter_name=adapter_name,
            gateway_ip=gateway_ip,
            dns_servers=dns_servers or [],
            message=message,
            recommendation=recommendation
        )
    
    def get_diagnostic_report(self) -> str:
        """Generar reporte de diagnóstico en texto"""
        result = self.run_full_diagnostic()
        
        lines = [
            "=" * 60,
            "NETBOOZT - NETWORK DIAGNOSTIC REPORT",
            f"Generated: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            f"Status: {result.health.value.upper()}",
            f"Failure Point: {result.failure_point.value}",
            "",
            "--- Connection Chain ---",
            f"[1] Adapter ({result.adapter_name}): {'✓ OK' if result.adapter_ok else '✗ FAIL'}",
            f"[2] Router ({result.gateway_ip}): {'✓ OK' if result.router_ok else '✗ FAIL'}" + 
                (f" ({result.router_latency_ms:.0f}ms)" if result.router_latency_ms else ""),
            f"[3] ISP/Internet: {'✓ OK' if result.isp_ok else '✗ FAIL'}" +
                (f" ({result.isp_latency_ms:.0f}ms)" if result.isp_latency_ms else ""),
            f"[4] DNS ({result.dns_servers[0] if result.dns_servers else 'N/A'}): {'✓ OK' if result.dns_ok else '✗ FAIL'}" +
                (f" ({result.dns_latency_ms:.0f}ms)" if result.dns_latency_ms else ""),
            "",
            "--- Diagnosis ---",
            result.message,
            "",
            "--- Recommendation ---",
            result.recommendation,
            "",
            "=" * 60,
        ]
        
        return "\n".join(lines)


# Singleton
_diagnostics_instance = None

def get_diagnostics() -> NetworkDiagnostics:
    """Obtener instancia del sistema de diagnóstico"""
    global _diagnostics_instance
    if _diagnostics_instance is None:
        _diagnostics_instance = NetworkDiagnostics()
    return _diagnostics_instance


if __name__ == "__main__":
    # Test
    diag = NetworkDiagnostics()
    
    print("Ejecutando diagnóstico completo...\n")
    print(diag.get_diagnostic_report())
