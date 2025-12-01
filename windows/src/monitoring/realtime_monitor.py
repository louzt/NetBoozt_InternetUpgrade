"""
NetBoozt - Network Monitor en Tiempo Real
Recolecta métricas de red y las almacena para gráficas

By LOUST (www.loust.pro)
"""

import psutil
import time
import threading
import subprocess
import platform
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
from collections import deque


class LatencyMonitor:
    """Monitor de latencia usando ping"""
    
    def __init__(self, target: str = "8.8.8.8"):
        """
        Args:
            target: IP o hostname para hacer ping (default: Google DNS)
        """
        self.target = target
        self._last_latency_ms = 0.0
        self._lock = threading.Lock()
    
    def measure_latency(self) -> float:
        """
        Medir latencia con ping
        
        Returns:
            Latencia en ms (0.0 si falla)
        """
        try:
            # Determinar comando según OS
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            
            # Ejecutar ping (1 paquete, timeout 1 segundo)
            result = subprocess.run(
                ['ping', param, '1', '-w', '1000', self.target],
                capture_output=True,
                text=True,
                timeout=2.0,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                # Parsear salida de ping
                output = result.stdout
                
                if platform.system().lower() == 'windows':
                    # Buscar "tiempo=XXms" o "time=XXms"
                    import re
                    match = re.search(r'tiempo[=<](\d+)ms|time[=<](\d+)ms', output, re.IGNORECASE)
                    if match:
                        latency = float(match.group(1) or match.group(2))
                        with self._lock:
                            self._last_latency_ms = latency
                        return latency
                else:
                    # Linux/Mac: buscar "time=XX.X ms"
                    import re
                    match = re.search(r'time=(\d+\.?\d*)\s*ms', output)
                    if match:
                        latency = float(match.group(1))
                        with self._lock:
                            self._last_latency_ms = latency
                        return latency
        
        except Exception as e:
            # Silenciar errores de ping (red caída, timeout, etc.)
            pass
        
        # Retornar último valor conocido si falla
        with self._lock:
            return self._last_latency_ms
    
    def get_last_latency(self) -> float:
        """Obtener última latencia medida"""
        with self._lock:
            return self._last_latency_ms


@dataclass
class NetworkSnapshot:
    """Snapshot de métricas de red en un momento"""
    timestamp: datetime
    adapter: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    speed_mbps: float
    
    # Calculados (desde snapshot anterior)
    download_rate_mbps: float = 0.0
    upload_rate_mbps: float = 0.0
    packets_sent_per_sec: float = 0.0
    packets_recv_per_sec: float = 0.0
    errors_per_sec: float = 0.0
    drops_per_sec: float = 0.0


class NetworkMonitor:
    """Monitor de red en tiempo real"""
    
    def __init__(self, adapter_name: str, interval: float = 1.0):
        """
        Args:
            adapter_name: Nombre del adaptador (ej: "Ethernet", "Wi-Fi")
            interval: Intervalo de muestreo en segundos
        """
        self.adapter_name = adapter_name
        self.interval = interval
        
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._ping_thread: Optional[threading.Thread] = None
        
        # Historial en memoria (últimos N snapshots)
        self.history: deque[NetworkSnapshot] = deque(maxlen=300)  # 5 min a 1s
        
        # Callbacks para notificaciones
        self.on_update_callbacks: List[Callable] = []
        
        # Último snapshot para calcular deltas
        self._last_snapshot: Optional[NetworkSnapshot] = None
        
        # Monitor de latencia
        self.latency_monitor = LatencyMonitor()
        self._current_latency_ms = 0.0
        
        # Thread safety
        self._lock = threading.Lock()
    
    def __del__(self):
        """Cleanup al destruir el objeto"""
        try:
            self.stop()
        except Exception:
            # Ignore errors during cleanup
            pass
    
    def start(self):
        """Iniciar monitoreo"""
        if self.is_running:
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        
        # Iniciar thread de ping (cada 2 segundos para no saturar)
        self._ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self._ping_thread.start()
    
    def stop(self):
        """Detener monitoreo"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._ping_thread:
            self._ping_thread.join(timeout=2.0)
    
    def _ping_loop(self):
        """Loop de medición de latencia"""
        while self.is_running:
            try:
                latency = self.latency_monitor.measure_latency()
                with self._lock:
                    self._current_latency_ms = latency
            except Exception as e:
                log_error(f"Error en ping: {e}")
            
            time.sleep(2.0)  # Ping cada 2 segundos
    
    def _monitor_loop(self):
        """Loop principal de monitoreo"""
        while self.is_running:
            try:
                snapshot = self._capture_snapshot()
                
                # Thread-safe append
                with self._lock:
                    self.history.append(snapshot)
                
                # Notificar callbacks
                for callback in self.on_update_callbacks:
                    try:
                        callback(snapshot)
                    except Exception as e:
                        log_error(f"Error en callback: {e}")
                
            except Exception as e:
                log_error(f"Error en monitor: {e}")
            
            time.sleep(self.interval)
    
    def _capture_snapshot(self) -> NetworkSnapshot:
        """Capturar snapshot actual"""
        # Obtener stats del adaptador
        net_io = psutil.net_io_counters(pernic=True)
        
        # Intentar encontrar el adaptador con diferentes variaciones
        adapter_found = None
        stats = None
        
        if self.adapter_name in net_io:
            # Nombre exacto
            adapter_found = self.adapter_name
            stats = net_io[self.adapter_name]
        else:
            # Buscar variaciones comunes (Ethernet vs Ethernet 0, Wi-Fi vs WiFi, etc.)
            for key in net_io.keys():
                if (self.adapter_name.lower() in key.lower() or 
                    key.lower() in self.adapter_name.lower()):
                    adapter_found = key
                    stats = net_io[key]
                    break
        
        if stats is None:
            # Adaptador no encontrado, usar stats totales
            try:
                from ..utils.logger import log_warning
                log_warning(f"Adaptador '{self.adapter_name}' no encontrado. Usando stats totales. Disponibles: {list(net_io.keys())}")
            except Exception:
                # Logger import puede fallar
                pass
            
            stats = psutil.net_io_counters()
            adapter_found = "All"
        
        # Crear snapshot
        snapshot = NetworkSnapshot(
            timestamp=datetime.now(),
            adapter=adapter_found,
            bytes_sent=stats.bytes_sent,
            bytes_recv=stats.bytes_recv,
            packets_sent=stats.packets_sent,
            packets_recv=stats.packets_recv,
            errors_in=stats.errin,
            errors_out=stats.errout,
            drops_in=stats.dropin,
            drops_out=stats.dropout,
            speed_mbps=self._get_adapter_speed(adapter_found)
        )
        
        # Calcular tasas de transferencia
        if self._last_snapshot:
            time_delta = (snapshot.timestamp - self._last_snapshot.timestamp).total_seconds()
            if time_delta > 0:
                bytes_sent_delta = snapshot.bytes_sent - self._last_snapshot.bytes_sent
                bytes_recv_delta = snapshot.bytes_recv - self._last_snapshot.bytes_recv
                
                # Convertir a Mbps
                snapshot.upload_rate_mbps = (bytes_sent_delta * 8) / (time_delta * 1_000_000)
                snapshot.download_rate_mbps = (bytes_recv_delta * 8) / (time_delta * 1_000_000)
                
                # Calcular packets per second
                packets_sent_delta = snapshot.packets_sent - self._last_snapshot.packets_sent
                packets_recv_delta = snapshot.packets_recv - self._last_snapshot.packets_recv
                snapshot.packets_sent_per_sec = packets_sent_delta / time_delta
                snapshot.packets_recv_per_sec = packets_recv_delta / time_delta
                
                # Calcular errores y drops per second
                errors_delta = (snapshot.errors_in + snapshot.errors_out) - (self._last_snapshot.errors_in + self._last_snapshot.errors_out)
                drops_delta = (snapshot.drops_in + snapshot.drops_out) - (self._last_snapshot.drops_in + self._last_snapshot.drops_out)
                snapshot.errors_per_sec = errors_delta / time_delta
                snapshot.drops_per_sec = drops_delta / time_delta
        
        self._last_snapshot = snapshot
        return snapshot
    
    def _get_adapter_speed(self, adapter_name: str) -> float:
        """Obtener velocidad del adaptador en Mbps"""
        try:
            if adapter_name == "All":
                return 1000.0  # Asumido
            
            # Obtener info del adaptador
            addrs = psutil.net_if_stats()
            if adapter_name in addrs:
                speed = addrs[adapter_name].speed
                return float(speed) if speed else 1000.0
        except Exception:
            # psutil error or adapter not found
            pass
        
        return 1000.0
    
    def get_current_snapshot(self) -> Optional[NetworkSnapshot]:
        """Obtener snapshot más reciente"""
        with self._lock:
            return self.history[-1] if self.history else None
    
    def get_history(self, seconds: int = 60) -> List[NetworkSnapshot]:
        """
        Obtener historial de los últimos N segundos
        
        Args:
            seconds: Segundos de historial
        
        Returns:
            Lista de snapshots
        """
        with self._lock:
            if not self.history:
                return []
            
            cutoff = datetime.now().timestamp() - seconds
            return [
                s for s in self.history 
                if s.timestamp.timestamp() >= cutoff
            ]
    
    def get_average_rates(self, seconds: int = 10) -> Dict[str, float]:
        """
        Calcular tasas promedio en los últimos N segundos
        
        Returns:
            {
                'download_mbps': float,
                'upload_mbps': float,
                'packets_per_sec': float
            }
        """
        recent = self.get_history(seconds)
        
        if not recent:
            return {
                'download_mbps': 0.0,
                'upload_mbps': 0.0,
                'packets_per_sec': 0.0
            }
        
        downloads = [s.download_rate_mbps for s in recent if s.download_rate_mbps > 0]
        uploads = [s.upload_rate_mbps for s in recent if s.upload_rate_mbps > 0]
        
        return {
            'download_mbps': sum(downloads) / len(downloads) if downloads else 0.0,
            'upload_mbps': sum(uploads) / len(uploads) if uploads else 0.0,
            'packets_per_sec': 0.0  # TODO: Calcular
        }
    
    def get_peak_rates(self, seconds: int = 60) -> Dict[str, float]:
        """Obtener picos de velocidad en los últimos N segundos"""
        recent = self.get_history(seconds)
        
        if not recent:
            return {
                'peak_download_mbps': 0.0,
                'peak_upload_mbps': 0.0
            }
        
        return {
            'peak_download_mbps': max((s.download_rate_mbps for s in recent), default=0.0),
            'peak_upload_mbps': max((s.upload_rate_mbps for s in recent), default=0.0)
        }
    
    def get_error_stats(self) -> Dict[str, int]:
        """Estadísticas de errores totales"""
        current = self.get_current_snapshot()
        
        if not current:
            return {
                'total_errors_in': 0,
                'total_errors_out': 0,
                'total_drops_in': 0,
                'total_drops_out': 0
            }
        
        return {
            'total_errors_in': current.errors_in,
            'total_errors_out': current.errors_out,
            'total_drops_in': current.drops_in,
            'total_drops_out': current.drops_out
        }
    
    def get_current_latency(self) -> float:
        """Obtener latencia actual en ms"""
        with self._lock:
            return self._current_latency_ms
    
    def get_average_latency(self, seconds: int = 10) -> float:
        """
        Calcular latencia promedio (aproximada basada en lecturas actuales)
        
        Note: Esta es una aproximación ya que no guardamos historial de latencia
        """
        with self._lock:
            return self._current_latency_ms
    
    def register_callback(self, callback: Callable[[NetworkSnapshot], None]):
        """Registrar callback para actualizaciones"""
        with self._lock:
            self.on_update_callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Eliminar callback"""
        if callback in self.on_update_callbacks:
            self.on_update_callbacks.remove(callback)


class MultiAdapterMonitor:
    """Monitor de múltiples adaptadores simultáneamente"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.monitors: Dict[str, NetworkMonitor] = {}
        
        # Detectar adaptadores disponibles
        self.detect_adapters()
    
    def detect_adapters(self):
        """Detectar adaptadores de red disponibles"""
        net_if = psutil.net_if_addrs()
        net_stats = psutil.net_if_stats()
        
        for adapter_name in net_if.keys():
            if adapter_name in net_stats and net_stats[adapter_name].isup:
                if adapter_name not in self.monitors:
                    self.monitors[adapter_name] = NetworkMonitor(
                        adapter_name, 
                        self.interval
                    )
    
    def start_all(self):
        """Iniciar monitoreo de todos los adaptadores"""
        for monitor in self.monitors.values():
            monitor.start()
    
    def stop_all(self):
        """Detener todos los monitores"""
        for monitor in self.monitors.values():
            monitor.stop()
    
    def get_monitor(self, adapter_name: str) -> Optional[NetworkMonitor]:
        """Obtener monitor de un adaptador específico"""
        return self.monitors.get(adapter_name)
    
    def get_all_snapshots(self) -> Dict[str, NetworkSnapshot]:
        """Obtener snapshot actual de todos los adaptadores"""
        return {
            name: monitor.get_current_snapshot()
            for name, monitor in self.monitors.items()
            if monitor.get_current_snapshot() is not None
        }
