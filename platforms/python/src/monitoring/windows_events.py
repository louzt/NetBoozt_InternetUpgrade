"""
NetBoozt - Windows Event Log Integration
Lee y monitorea eventos de red del sistema operativo

By LOUST (www.loust.pro)
"""

import subprocess
import threading
import time
import json
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

try:
    from ..utils.logger import log_info, log_warning, log_error
except ImportError:
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")
    def log_error(msg): print(f"[ERROR] {msg}")


class NetworkEventType(Enum):
    """Tipos de eventos de red de Windows"""
    DNS_TIMEOUT = "dns_timeout"
    DNS_FAILURE = "dns_failure"
    WLAN_DISCONNECT = "wlan_disconnect"
    WLAN_CONNECT = "wlan_connect"
    WLAN_LIMITED = "wlan_limited"
    ADAPTER_ERROR = "adapter_error"
    NCSI_FAILURE = "ncsi_failure"  # Network Connectivity Status Indicator
    TCP_RESET = "tcp_reset"
    DHCP_FAILURE = "dhcp_failure"


@dataclass
class WindowsNetworkEvent:
    """Evento de red de Windows"""
    event_type: NetworkEventType
    timestamp: datetime
    provider: str
    level: str  # Error, Warning, Information
    message: str
    event_id: int
    details: Dict = None


class WindowsEventMonitor:
    """Monitor de eventos de red de Windows Event Log"""
    
    # Providers de red importantes
    NETWORK_PROVIDERS = [
        'Microsoft-Windows-WLAN-AutoConfig',
        'Microsoft-Windows-DNS-Client',
        'Microsoft-Windows-NCSI',
        'Microsoft-Windows-NetworkProfile',
        'Microsoft-Windows-Dhcp-Client',
        'Tcpip',
    ]
    
    # Event IDs importantes
    IMPORTANT_EVENTS = {
        # DNS Client
        1014: NetworkEventType.DNS_TIMEOUT,   # DNS timeout
        1015: NetworkEventType.DNS_FAILURE,   # DNS failure
        
        # WLAN
        8000: NetworkEventType.WLAN_DISCONNECT,  # Desconectado de red
        8001: NetworkEventType.WLAN_CONNECT,     # Conectado a red
        8002: NetworkEventType.WLAN_LIMITED,     # Conectividad limitada
        11004: NetworkEventType.WLAN_DISCONNECT, # Association failure
        
        # NCSI
        4042: NetworkEventType.NCSI_FAILURE,     # No internet
        
        # DHCP
        1002: NetworkEventType.DHCP_FAILURE,     # DHCP timeout
    }
    
    def __init__(self, lookback_hours: int = 1, poll_interval: int = 30):
        """
        Args:
            lookback_hours: Horas hacia atrás para buscar eventos iniciales
            poll_interval: Segundos entre verificaciones de nuevos eventos
        """
        self.lookback_hours = lookback_hours
        self.poll_interval = poll_interval
        
        self.events: List[WindowsNetworkEvent] = []
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[WindowsNetworkEvent], None]] = []
        self._lock = threading.Lock()
        
        self._last_check = datetime.now() - timedelta(hours=lookback_hours)
    
    def start(self):
        """Iniciar monitoreo de eventos"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Cargar eventos históricos
        self._load_recent_events()
        
        # Iniciar thread de monitoreo
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        
        log_info(f"Windows Event Monitor iniciado (lookback: {self.lookback_hours}h)")
    
    def stop(self):
        """Detener monitoreo"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        log_info("Windows Event Monitor detenido")
    
    def on_event(self, callback: Callable[[WindowsNetworkEvent], None]):
        """Registrar callback para nuevos eventos"""
        self._callbacks.append(callback)
    
    def _monitor_loop(self):
        """Loop de monitoreo de nuevos eventos"""
        while self.is_running:
            try:
                self._check_new_events()
                time.sleep(self.poll_interval)
            except Exception as e:
                log_error(f"Error en event monitor loop: {e}")
                time.sleep(10)
    
    def _load_recent_events(self):
        """Cargar eventos recientes del Event Log"""
        try:
            start_time = datetime.now() - timedelta(hours=self.lookback_hours)
            events = self._query_events(start_time)
            
            with self._lock:
                self.events = events
            
            log_info(f"Cargados {len(events)} eventos de red recientes")
            
        except Exception as e:
            log_error(f"Error cargando eventos recientes: {e}")
    
    def _check_new_events(self):
        """Verificar eventos nuevos desde última verificación"""
        try:
            new_events = self._query_events(self._last_check)
            self._last_check = datetime.now()
            
            if new_events:
                with self._lock:
                    self.events.extend(new_events)
                    # Mantener solo últimas 1000 entradas
                    if len(self.events) > 1000:
                        self.events = self.events[-1000:]
                
                # Notificar callbacks
                for event in new_events:
                    self._notify_event(event)
                    
        except Exception as e:
            log_error(f"Error verificando nuevos eventos: {e}")
    
    def _query_events(self, since: datetime) -> List[WindowsNetworkEvent]:
        """Consultar Event Log de Windows"""
        events = []
        
        try:
            # Formatear fecha para PowerShell
            since_str = since.strftime("%Y-%m-%dT%H:%M:%S")
            
            # Query PowerShell
            providers_filter = "','".join(self.NETWORK_PROVIDERS)
            
            cmd = f"""
            $events = Get-WinEvent -FilterHashtable @{{
                LogName='System';
                ProviderName='{providers_filter}'.Split(',');
                Level=2,3;
                StartTime='{since_str}'
            }} -MaxEvents 100 -ErrorAction SilentlyContinue
            
            $events | ForEach-Object {{
                [PSCustomObject]@{{
                    TimeCreated = $_.TimeCreated.ToString('yyyy-MM-ddTHH:mm:ss')
                    ProviderName = $_.ProviderName
                    Level = $_.LevelDisplayName
                    Id = $_.Id
                    Message = $_.Message.Substring(0, [Math]::Min(500, $_.Message.Length))
                }}
            }} | ConvertTo-Json -Compress
            """
            
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.stdout.strip():
                data = json.loads(result.stdout)
                
                # Asegurar que sea lista
                if isinstance(data, dict):
                    data = [data]
                
                for item in data:
                    event_type = self._classify_event(item)
                    if event_type:
                        events.append(WindowsNetworkEvent(
                            event_type=event_type,
                            timestamp=datetime.fromisoformat(item['TimeCreated']),
                            provider=item['ProviderName'],
                            level=item['Level'],
                            message=item['Message'],
                            event_id=item['Id']
                        ))
                        
        except json.JSONDecodeError:
            pass  # Sin eventos
        except subprocess.TimeoutExpired:
            log_warning("Timeout consultando Event Log")
        except Exception as e:
            log_error(f"Error en query de eventos: {e}")
        
        return events
    
    def _classify_event(self, event_data: dict) -> Optional[NetworkEventType]:
        """Clasificar evento por ID o contenido"""
        event_id = event_data.get('Id', 0)
        message = event_data.get('Message', '').lower()
        provider = event_data.get('ProviderName', '')
        
        # Por Event ID conocido
        if event_id in self.IMPORTANT_EVENTS:
            return self.IMPORTANT_EVENTS[event_id]
        
        # Por contenido del mensaje
        if 'dns' in provider.lower() or 'dns' in message:
            if 'timeout' in message or 'agotó' in message or 'tiempo de espera' in message:
                return NetworkEventType.DNS_TIMEOUT
            if 'fail' in message or 'error' in message:
                return NetworkEventType.DNS_FAILURE
        
        if 'wlan' in provider.lower():
            if 'disconnect' in message or 'desconect' in message:
                return NetworkEventType.WLAN_DISCONNECT
            if 'limited' in message or 'limitado' in message or 'limitada' in message:
                return NetworkEventType.WLAN_LIMITED
            if 'connect' in message or 'conectado' in message:
                return NetworkEventType.WLAN_CONNECT
        
        return None
    
    def _notify_event(self, event: WindowsNetworkEvent):
        """Notificar callbacks de nuevo evento"""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                log_error(f"Error en callback de evento: {e}")
    
    def get_events(self, event_type: Optional[NetworkEventType] = None, 
                   hours: int = 1) -> List[WindowsNetworkEvent]:
        """Obtener eventos filtrados"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            filtered = [e for e in self.events if e.timestamp >= cutoff]
            
            if event_type:
                filtered = [e for e in filtered if e.event_type == event_type]
            
            return filtered
    
    def get_dns_timeout_count(self, minutes: int = 5) -> int:
        """Contar timeouts DNS en últimos N minutos"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            return sum(1 for e in self.events 
                      if e.timestamp >= cutoff and 
                      e.event_type in (NetworkEventType.DNS_TIMEOUT, NetworkEventType.DNS_FAILURE))
    
    def get_wlan_disconnects(self, hours: int = 1) -> List[WindowsNetworkEvent]:
        """Obtener desconexiones WiFi"""
        return self.get_events(NetworkEventType.WLAN_DISCONNECT, hours)
    
    def get_summary(self) -> Dict:
        """Resumen de eventos recientes"""
        with self._lock:
            last_hour = datetime.now() - timedelta(hours=1)
            recent = [e for e in self.events if e.timestamp >= last_hour]
            
            by_type = {}
            for event in recent:
                type_name = event.event_type.value
                by_type[type_name] = by_type.get(type_name, 0) + 1
            
            return {
                'total_events_last_hour': len(recent),
                'by_type': by_type,
                'dns_timeouts_5min': self.get_dns_timeout_count(5),
                'dns_timeouts_1hour': sum(1 for e in recent 
                                          if e.event_type == NetworkEventType.DNS_TIMEOUT),
                'wlan_issues': sum(1 for e in recent 
                                   if e.event_type in (NetworkEventType.WLAN_DISCONNECT, 
                                                       NetworkEventType.WLAN_LIMITED))
            }


# Singleton
_event_monitor_instance = None

def get_event_monitor() -> WindowsEventMonitor:
    """Obtener instancia única del monitor de eventos"""
    global _event_monitor_instance
    if _event_monitor_instance is None:
        _event_monitor_instance = WindowsEventMonitor()
    return _event_monitor_instance


if __name__ == "__main__":
    # Test
    monitor = WindowsEventMonitor(lookback_hours=24)
    
    def on_new_event(event):
        print(f"🔔 {event.event_type.value}: {event.message[:80]}...")
    
    monitor.on_event(on_new_event)
    monitor.start()
    
    try:
        print("\nMonitoreando eventos de red (Ctrl+C para salir)...\n")
        
        # Mostrar resumen inicial
        summary = monitor.get_summary()
        print(f"📊 Resumen última hora:")
        print(f"   Total eventos: {summary['total_events_last_hour']}")
        print(f"   DNS timeouts (5min): {summary['dns_timeouts_5min']}")
        print(f"   DNS timeouts (1h): {summary['dns_timeouts_1hour']}")
        print(f"   Problemas WiFi: {summary['wlan_issues']}")
        print(f"\n   Por tipo: {summary['by_type']}")
        
        while True:
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    finally:
        monitor.stop()
