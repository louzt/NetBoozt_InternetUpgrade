"""
NetBoozt - Monitoring Module
Monitoreo en tiempo real de red y gestión de adaptadores

Includes:
- Real-time network monitoring
- Adapter management
- DNS health checking
- Auto-failover system
- Windows event log integration
- Network diagnostics
"""

from .realtime_monitor import NetworkMonitor, NetworkSnapshot, MultiAdapterMonitor
from .adapter_manager import AdapterManager, NetworkAdapter, DNSFallbackTier, get_adapter_manager
from .dns_health import DNSHealthChecker, DNSHealth, DNSStatus
from .alert_system import AlertSystem, Alert, AlertType, AlertSeverity, get_alert_system
from .auto_failover import AutoFailoverManager, FailoverEvent
from .windows_events import WindowsEventMonitor, WindowsNetworkEvent, NetworkEventType, get_event_monitor
from .network_diagnostics import NetworkDiagnostics, DiagnosticResult, FailurePoint, NetworkHealth, get_diagnostics

__all__ = [
    # Real-time monitoring
    'NetworkMonitor', 
    'NetworkSnapshot', 
    'MultiAdapterMonitor',
    
    # Adapter management
    'AdapterManager',
    'NetworkAdapter',
    'DNSFallbackTier',
    'get_adapter_manager',
    
    # DNS health
    'DNSHealthChecker',
    'DNSHealth',
    'DNSStatus',
    
    # Alert system
    'AlertSystem',
    'Alert',
    'AlertType',
    'AlertSeverity',
    'get_alert_system',
    
    # Auto-failover
    'AutoFailoverManager',
    'FailoverEvent',
    
    # Windows events
    'WindowsEventMonitor',
    'WindowsNetworkEvent',
    'NetworkEventType',
    'get_event_monitor',
    
    # Network diagnostics
    'NetworkDiagnostics',
    'DiagnosticResult',
    'FailurePoint',
    'NetworkHealth',
    'get_diagnostics',
]
