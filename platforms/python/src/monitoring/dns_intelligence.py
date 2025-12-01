"""
DNS Intelligence System - Smart DNS Selection with Historical Analysis

Este módulo implementa un sistema inteligente de selección de DNS que:
1. Analiza rendimiento en paralelo de múltiples DNS
2. Mantiene histórico de salud/rendimiento
3. Selecciona automáticamente el mejor DNS basado en datos reales
4. Consume recursos mínimos como servicio de fondo

By LOUST (www.loust.pro)
"""

import threading
import time
import json
import statistics
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import socket


@dataclass
class DNSMetrics:
    """Métricas de un servidor DNS."""
    address: str
    name: str
    
    # Métricas actuales
    ping_ms: float = 0.0
    resolve_ms: float = 0.0
    success_rate: float = 100.0
    last_check: Optional[str] = None
    is_healthy: bool = True
    
    # Histórico (últimas 24h)
    avg_ping_24h: float = 0.0
    avg_resolve_24h: float = 0.0
    uptime_24h: float = 100.0
    checks_24h: int = 0
    failures_24h: int = 0
    
    # Score calculado (0-100)
    score: float = 50.0
    rank: int = 0


@dataclass 
class DNSHistoryEntry:
    """Entrada de histórico de DNS."""
    timestamp: str
    address: str
    ping_ms: float
    resolve_ms: float
    success: bool


class DNSIntelligence:
    """
    Sistema inteligente de DNS que analiza y rankea servidores
    basándose en rendimiento real medido en paralelo.
    """
    
    # Servidores DNS a monitorear
    DNS_SERVERS = {
        "1.1.1.1": "Cloudflare",
        "1.0.0.1": "Cloudflare Secondary",
        "8.8.8.8": "Google",
        "8.8.4.4": "Google Secondary",
        "9.9.9.9": "Quad9",
        "149.112.112.112": "Quad9 Secondary",
        "208.67.222.222": "OpenDNS",
        "208.67.220.220": "OpenDNS Secondary",
        "94.140.14.14": "AdGuard",
        "94.140.15.15": "AdGuard Secondary",
        "185.228.168.9": "CleanBrowsing",
    }
    
    # Dominios de prueba para resolución
    TEST_DOMAINS = [
        "google.com",
        "cloudflare.com", 
        "microsoft.com",
        "amazon.com",
    ]
    
    # Configuración
    CHECK_INTERVAL_SECONDS = 300  # 5 minutos entre checks (bajo consumo)
    HISTORY_RETENTION_HOURS = 24
    MAX_HISTORY_ENTRIES = 1000
    PARALLEL_WORKERS = 4  # Threads paralelos para checks
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".netboozt"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.data_dir / "dns_history.json"
        self.metrics_file = self.data_dir / "dns_metrics.json"
        
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[Dict[str, DNSMetrics]], None]] = []
        
        # Estado actual
        self.metrics: Dict[str, DNSMetrics] = {}
        self.history: List[DNSHistoryEntry] = []
        
        # Inicializar métricas
        self._init_metrics()
        self._load_history()
    
    def _init_metrics(self):
        """Inicializa métricas para todos los DNS."""
        for addr, name in self.DNS_SERVERS.items():
            self.metrics[addr] = DNSMetrics(address=addr, name=name)
    
    def _load_history(self):
        """Carga historial desde disco."""
        try:
            if self.history_file.exists():
                data = json.loads(self.history_file.read_text())
                self.history = [DNSHistoryEntry(**entry) for entry in data]
                # Limpiar entradas antiguas
                self._cleanup_history()
        except Exception:
            self.history = []
    
    def _save_history(self):
        """Guarda historial a disco."""
        try:
            with self._lock:
                data = [asdict(entry) for entry in self.history[-self.MAX_HISTORY_ENTRIES:]]
            self.history_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass
    
    def _cleanup_history(self):
        """Elimina entradas más antiguas que HISTORY_RETENTION_HOURS."""
        cutoff = datetime.now() - timedelta(hours=self.HISTORY_RETENTION_HOURS)
        cutoff_str = cutoff.isoformat()
        
        with self._lock:
            self.history = [
                entry for entry in self.history 
                if entry.timestamp > cutoff_str
            ]
    
    def _ping_dns(self, address: str, timeout: float = 2.0) -> Tuple[bool, float]:
        """
        Ping a un servidor DNS.
        Returns: (success, latency_ms)
        """
        try:
            # Usar socket para TCP connect (más confiable que ICMP)
            start = time.perf_counter()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((address, 53))
            elapsed = (time.perf_counter() - start) * 1000
            sock.close()
            
            if result == 0:
                return True, elapsed
            return False, 0.0
        except Exception:
            return False, 0.0
    
    def _resolve_dns(self, address: str, domain: str, timeout: float = 2.0) -> Tuple[bool, float]:
        """
        Resuelve un dominio usando un DNS específico.
        Returns: (success, latency_ms)
        """
        try:
            # Usar nslookup para resolución específica
            start = time.perf_counter()
            result = subprocess.run(
                ["nslookup", domain, address],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            elapsed = (time.perf_counter() - start) * 1000
            
            # Verificar si resolvió correctamente
            if result.returncode == 0 and "Address" in result.stdout:
                return True, elapsed
            return False, elapsed
        except Exception:
            return False, 0.0
    
    def _check_single_dns(self, address: str) -> Tuple[str, bool, float, float]:
        """
        Verifica un DNS individual.
        Returns: (address, success, ping_ms, resolve_ms)
        """
        # Ping
        ping_ok, ping_ms = self._ping_dns(address)
        if not ping_ok:
            return address, False, 0.0, 0.0
        
        # Resolver un dominio aleatorio de la lista
        import random
        domain = random.choice(self.TEST_DOMAINS)
        resolve_ok, resolve_ms = self._resolve_dns(address, domain)
        
        return address, resolve_ok, ping_ms, resolve_ms
    
    def check_all_parallel(self) -> Dict[str, DNSMetrics]:
        """
        Verifica todos los DNS en paralelo.
        Actualiza métricas y retorna resultados.
        """
        results = {}
        timestamp = datetime.now().isoformat()
        
        # Ejecutar checks en paralelo
        with ThreadPoolExecutor(max_workers=self.PARALLEL_WORKERS) as executor:
            futures = {
                executor.submit(self._check_single_dns, addr): addr 
                for addr in self.DNS_SERVERS.keys()
            }
            
            for future in as_completed(futures):
                try:
                    addr, success, ping_ms, resolve_ms = future.result()
                    
                    # Actualizar métricas
                    with self._lock:
                        metrics = self.metrics[addr]
                        metrics.ping_ms = ping_ms
                        metrics.resolve_ms = resolve_ms
                        metrics.is_healthy = success
                        metrics.last_check = timestamp
                        
                        # Agregar al historial
                        entry = DNSHistoryEntry(
                            timestamp=timestamp,
                            address=addr,
                            ping_ms=ping_ms,
                            resolve_ms=resolve_ms,
                            success=success
                        )
                        self.history.append(entry)
                        
                        results[addr] = metrics
                        
                except Exception:
                    pass
        
        # Calcular estadísticas 24h y scores
        self._calculate_stats()
        self._calculate_scores()
        
        # Guardar historial
        self._save_history()
        
        # Notificar callbacks
        self._notify_callbacks()
        
        return self.metrics.copy()
    
    def _calculate_stats(self):
        """Calcula estadísticas de las últimas 24h para cada DNS."""
        cutoff = datetime.now() - timedelta(hours=24)
        cutoff_str = cutoff.isoformat()
        
        with self._lock:
            for addr in self.DNS_SERVERS.keys():
                # Filtrar historial para este DNS
                entries = [
                    e for e in self.history 
                    if e.address == addr and e.timestamp > cutoff_str
                ]
                
                if not entries:
                    continue
                
                metrics = self.metrics[addr]
                metrics.checks_24h = len(entries)
                metrics.failures_24h = sum(1 for e in entries if not e.success)
                
                # Calcular promedios (solo de checks exitosos)
                successful = [e for e in entries if e.success]
                if successful:
                    metrics.avg_ping_24h = statistics.mean(e.ping_ms for e in successful)
                    metrics.avg_resolve_24h = statistics.mean(e.resolve_ms for e in successful)
                
                # Uptime
                if entries:
                    metrics.uptime_24h = (len(successful) / len(entries)) * 100
                    metrics.success_rate = metrics.uptime_24h
    
    def _calculate_scores(self):
        """
        Calcula score de calidad para cada DNS (0-100).
        
        Fórmula:
        - 40% basado en latencia de ping (menor = mejor)
        - 30% basado en latencia de resolución (menor = mejor)
        - 30% basado en uptime 24h
        """
        with self._lock:
            # Obtener rangos para normalización
            all_pings = [m.avg_ping_24h for m in self.metrics.values() if m.avg_ping_24h > 0]
            all_resolves = [m.avg_resolve_24h for m in self.metrics.values() if m.avg_resolve_24h > 0]
            
            if not all_pings or not all_resolves:
                return
            
            max_ping = max(all_pings) if all_pings else 100
            max_resolve = max(all_resolves) if all_resolves else 500
            
            for metrics in self.metrics.values():
                if metrics.avg_ping_24h == 0:
                    metrics.score = 0
                    continue
                
                # Normalizar (invertido: menor latencia = mayor score)
                ping_score = max(0, 100 - (metrics.avg_ping_24h / max_ping * 100)) if max_ping > 0 else 50
                resolve_score = max(0, 100 - (metrics.avg_resolve_24h / max_resolve * 100)) if max_resolve > 0 else 50
                uptime_score = metrics.uptime_24h
                
                # Score ponderado
                metrics.score = (
                    ping_score * 0.40 +
                    resolve_score * 0.30 +
                    uptime_score * 0.30
                )
            
            # Calcular ranking
            sorted_metrics = sorted(
                self.metrics.values(), 
                key=lambda m: m.score, 
                reverse=True
            )
            for i, m in enumerate(sorted_metrics):
                m.rank = i + 1
    
    def get_best_dns(self, count: int = 2) -> List[DNSMetrics]:
        """Obtiene los mejores DNS según score."""
        with self._lock:
            sorted_dns = sorted(
                self.metrics.values(),
                key=lambda m: m.score,
                reverse=True
            )
            return sorted_dns[:count]
    
    def get_ranking(self) -> List[DNSMetrics]:
        """Obtiene ranking completo de DNS."""
        with self._lock:
            return sorted(
                list(self.metrics.values()),
                key=lambda m: m.score,
                reverse=True
            )
    
    def on_update(self, callback: Callable[[Dict[str, DNSMetrics]], None]):
        """Registra callback para cuando se actualicen métricas."""
        self._callbacks.append(callback)
    
    def _notify_callbacks(self):
        """Notifica a todos los callbacks."""
        metrics_copy = self.metrics.copy()
        for cb in self._callbacks:
            try:
                cb(metrics_copy)
            except Exception:
                pass
    
    def start(self):
        """Inicia el servicio de monitoreo en segundo plano."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Detiene el servicio de monitoreo."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
    
    def _background_loop(self):
        """Loop de monitoreo en segundo plano."""
        # Check inicial
        self.check_all_parallel()
        
        while self._running:
            time.sleep(self.CHECK_INTERVAL_SECONDS)
            if self._running:
                try:
                    self.check_all_parallel()
                except Exception:
                    pass
    
    def get_summary(self) -> dict:
        """Obtiene resumen del estado actual."""
        best = self.get_best_dns(3)
        
        return {
            "best_dns": [
                {
                    "address": m.address,
                    "name": m.name,
                    "score": round(m.score, 1),
                    "ping_ms": round(m.avg_ping_24h, 1),
                    "resolve_ms": round(m.avg_resolve_24h, 1),
                    "uptime": round(m.uptime_24h, 1),
                }
                for m in best
            ],
            "total_dns_monitored": len(self.metrics),
            "history_entries": len(self.history),
            "last_check": max(
                (m.last_check for m in self.metrics.values() if m.last_check),
                default=None
            ),
        }


# Singleton
_instance: Optional[DNSIntelligence] = None


def get_dns_intelligence() -> DNSIntelligence:
    """Obtiene instancia única del sistema de inteligencia DNS."""
    global _instance
    if _instance is None:
        _instance = DNSIntelligence()
    return _instance


if __name__ == "__main__":
    # Test
    intel = get_dns_intelligence()
    print("Checking all DNS in parallel...")
    intel.check_all_parallel()
    
    print("\n📊 DNS Ranking:")
    for dns in intel.get_ranking():
        status = "✅" if dns.is_healthy else "❌"
        print(f"  {dns.rank}. {status} {dns.name} ({dns.address})")
        print(f"      Score: {dns.score:.1f} | Ping: {dns.ping_ms:.1f}ms | Resolve: {dns.resolve_ms:.1f}ms")
    
    print("\n🏆 Best DNS:")
    for dns in intel.get_best_dns(2):
        print(f"  • {dns.name} ({dns.address}) - Score: {dns.score:.1f}")
