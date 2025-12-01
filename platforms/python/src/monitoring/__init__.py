"""
NetBoozt - Monitoring Module
Monitoreo en tiempo real de red y gestión de adaptadores

Includes:
- Real-time network monitoring
- Adapter management
- DNS health checking
- DNS Intelligence (parallel analysis)
- Auto-failover system
- Windows event log integration
- Network diagnostics
"""

from .realtime_monitor import NetworkMonitor, NetworkSnapshot, MultiAdapterMonitor
from .adapter_manager import AdapterManager, NetworkAdapter, DNSFallbackTier, get_adapter_manager
from .dns_health import DNSHealthChecker, DNSHealth, DNSStatus
from .dns_intelligence import DNSIntelligence, DNSMetrics, get_dns_intelligence
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
    
    # DNS Intelligence (NEW v2.2)
    'DNSIntelligence',
    'DNSMetrics',
    'get_dns_intelligence',
    
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
