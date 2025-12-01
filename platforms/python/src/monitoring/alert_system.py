"""
NetBoozt - Sistema de Alertas Configurable
Monitorea métricas y dispara alertas cuando se superan thresholds

By LOUST (www.loust.pro)
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import threading
import time

try:
    from ..utils.logger import log_info, log_warning, log_error
    from ..utils.notifications import get_notification_manager
except ImportError:
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")
    def log_error(msg): print(f"[ERROR] {msg}")
    get_notification_manager = None


class AlertType(Enum):
    """Tipos de alerta"""
    LATENCY_HIGH = "latency_high"
    PACKET_LOSS_HIGH = "packet_loss_high"
    SPEED_LOW = "speed_low"
    DNS_FAILURE = "dns_failure"
    ADAPTER_ERROR = "adapter_error"
    MEMORY_HIGH = "memory_high"


class AlertSeverity(Enum):
    """Severidad de alerta"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertThreshold:
    """Configuración de threshold"""
    alert_type: AlertType
    threshold_value: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5  # No repetir alerta en X minutos


@dataclass
class Alert:
    """Alerta disparada"""
    alert_type: AlertType
    severity: AlertSeverity
    timestamp: datetime
    message: str
    current_value: float
    threshold_value: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AlertSystem:
    """Sistema de alertas configurable"""
    
    DEFAULT_THRESHOLDS = {
        AlertType.LATENCY_HIGH: AlertThreshold(
            alert_type=AlertType.LATENCY_HIGH,
            threshold_value=100.0,  # ms
            severity=AlertSeverity.WARNING,
            cooldown_minutes=5
        ),
        AlertType.PACKET_LOSS_HIGH: AlertThreshold(
            alert_type=AlertType.PACKET_LOSS_HIGH,
            threshold_value=2.0,  # %
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=3
        ),
        AlertType.SPEED_LOW: AlertThreshold(
            alert_type=AlertType.SPEED_LOW,
            threshold_value=10.0,  # Mbps
            severity=AlertSeverity.WARNING,
            cooldown_minutes=10
        ),
        AlertType.DNS_FAILURE: AlertThreshold(
            alert_type=AlertType.DNS_FAILURE,
            threshold_value=3.0,  # fallos consecutivos
            severity=AlertSeverity.CRITICAL,
            cooldown_minutes=2
        ),
        AlertType.ADAPTER_ERROR: AlertThreshold(
            alert_type=AlertType.ADAPTER_ERROR,
            threshold_value=10.0,  # errores/min
            severity=AlertSeverity.WARNING,
            cooldown_minutes=5
        ),
        AlertType.MEMORY_HIGH: AlertThreshold(
            alert_type=AlertType.MEMORY_HIGH,
            threshold_value=80.0,  # % uso
            severity=AlertSeverity.INFO,
            cooldown_minutes=15
        )
    }
    
    def __init__(self):
        self.thresholds: Dict[AlertType, AlertThreshold] = self.DEFAULT_THRESHOLDS.copy()
        self.alerts_history: List[Alert] = []
        self.last_alert_time: Dict[AlertType, datetime] = {}
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
        
        # Configuración
        self.max_history_size = 1000
        self.auto_resolve_after_minutes = 30
    
    def set_threshold(self, alert_type: AlertType, threshold_value: float, 
                     severity: AlertSeverity = None, cooldown_minutes: int = None):
        """Configurar threshold personalizado"""
        with self._lock:
            if alert_type in self.thresholds:
                threshold = self.thresholds[alert_type]
                threshold.threshold_value = threshold_value
                
                if severity:
                    threshold.severity = severity
                if cooldown_minutes is not None:
                    threshold.cooldown_minutes = cooldown_minutes
                
                log_info(f"Threshold actualizado: {alert_type.value} = {threshold_value}")
    
    def enable_alert(self, alert_type: AlertType, enabled: bool = True):
        """Habilitar/deshabilitar tipo de alerta"""
        with self._lock:
            if alert_type in self.thresholds:
                self.thresholds[alert_type].enabled = enabled
                status = "habilitada" if enabled else "deshabilitada"
                log_info(f"Alerta {alert_type.value} {status}")
    
    def check_metric(self, alert_type: AlertType, current_value: float) -> Optional[Alert]:
        """Verificar métrica contra threshold"""
        with self._lock:
            if alert_type not in self.thresholds:
                return None
            
            threshold = self.thresholds[alert_type]
            
            # Verificar si está habilitada
            if not threshold.enabled:
                return None
            
            # Verificar si supera threshold
            if current_value <= threshold.threshold_value:
                # Valor OK - resolver alerta si existe
                self._auto_resolve_alert(alert_type)
                return None
            
            # Verificar cooldown
            if not self._can_trigger_alert(alert_type):
                return None
            
            # Crear alerta
            alert = Alert(
                alert_type=alert_type,
                severity=threshold.severity,
                timestamp=datetime.now(),
                message=self._generate_message(alert_type, current_value, threshold.threshold_value),
                current_value=current_value,
                threshold_value=threshold.threshold_value
            )
            
            # Guardar en historial
            self.alerts_history.append(alert)
            self._trim_history()
            
            # Actualizar último trigger
            self.last_alert_time[alert_type] = alert.timestamp
            
            # Notificar
            self._notify_alert(alert)
            
            log_warning(f"Alerta disparada: {alert.message}")
            
            return alert
    
    def _can_trigger_alert(self, alert_type: AlertType) -> bool:
        """Verificar si puede disparar alerta (cooldown)"""
        if alert_type not in self.last_alert_time:
            return True
        
        threshold = self.thresholds[alert_type]
        last_time = self.last_alert_time[alert_type]
        cooldown = timedelta(minutes=threshold.cooldown_minutes)
        
        return datetime.now() - last_time >= cooldown
    
    def _auto_resolve_alert(self, alert_type: AlertType):
        """Auto-resolver alerta cuando valor vuelve a la normalidad"""
        now = datetime.now()
        
        for alert in reversed(self.alerts_history):
            if alert.alert_type == alert_type and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = now
                log_info(f"Alerta auto-resuelta: {alert_type.value}")
                break
    
    def _generate_message(self, alert_type: AlertType, current: float, threshold: float) -> str:
        """Generar mensaje de alerta"""
        messages = {
            AlertType.LATENCY_HIGH: f"Latencia alta: {current:.1f}ms (límite: {threshold:.1f}ms)",
            AlertType.PACKET_LOSS_HIGH: f"Pérdida de paquetes: {current:.1f}% (límite: {threshold:.1f}%)",
            AlertType.SPEED_LOW: f"Velocidad baja: {current:.1f} Mbps (mínimo: {threshold:.1f} Mbps)",
            AlertType.DNS_FAILURE: f"Fallo DNS: {int(current)} intentos fallidos",
            AlertType.ADAPTER_ERROR: f"Errores de adaptador: {current:.1f}/min (límite: {threshold:.1f}/min)",
            AlertType.MEMORY_HIGH: f"Uso de memoria alto: {current:.1f}% (límite: {threshold:.1f}%)"
        }
        
        return messages.get(alert_type, f"{alert_type.value}: {current} > {threshold}")
    
    def _notify_alert(self, alert: Alert):
        """Enviar notificación de alerta"""
        # Notificación del sistema
        if get_notification_manager:
            notif = get_notification_manager()
            if notif:
                icon = "🔴" if alert.severity == AlertSeverity.CRITICAL else "⚠️"
                notif.notify_alert(
                    alert_type=alert.alert_type.value,
                    details=alert.message
                )
        
        # Callbacks personalizados
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                log_error(f"Error en alert callback: {e}")
    
    def on_alert(self, callback: Callable):
        """Registrar callback para alertas"""
        self._callbacks.append(callback)
    
    def get_active_alerts(self) -> List[Alert]:
        """Obtener alertas activas (no resueltas)"""
        with self._lock:
            return [a for a in self.alerts_history if not a.resolved]
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Obtener alertas recientes"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            return [a for a in self.alerts_history if a.timestamp >= cutoff]
    
    def get_alerts_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Obtener alertas por tipo"""
        with self._lock:
            return [a for a in self.alerts_history if a.alert_type == alert_type]
    
    def resolve_alert(self, alert: Alert):
        """Marcar alerta como resuelta manualmente"""
        with self._lock:
            if not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                log_info(f"Alerta resuelta manualmente: {alert.alert_type.value}")
    
    def clear_history(self):
        """Limpiar historial de alertas"""
        with self._lock:
            self.alerts_history.clear()
            self.last_alert_time.clear()
            log_info("Historial de alertas limpiado")
    
    def _trim_history(self):
        """Mantener tamaño del historial bajo control"""
        if len(self.alerts_history) > self.max_history_size:
            # Mantener solo las más recientes
            self.alerts_history = self.alerts_history[-self.max_history_size:]
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de alertas"""
        with self._lock:
            total = len(self.alerts_history)
            active = len([a for a in self.alerts_history if not a.resolved])
            
            by_type = {}
            by_severity = {}
            
            for alert in self.alerts_history:
                # Por tipo
                type_key = alert.alert_type.value
                by_type[type_key] = by_type.get(type_key, 0) + 1
                
                # Por severidad
                sev_key = alert.severity.value
                by_severity[sev_key] = by_severity.get(sev_key, 0) + 1
            
            return {
                'total_alerts': total,
                'active_alerts': active,
                'resolved_alerts': total - active,
                'by_type': by_type,
                'by_severity': by_severity
            }


# Singleton global
_alert_system: Optional[AlertSystem] = None


def get_alert_system() -> AlertSystem:
    """Obtener instancia global del sistema de alertas"""
    global _alert_system
    
    if _alert_system is None:
        _alert_system = AlertSystem()
    
    return _alert_system


if __name__ == "__main__":
    # Test
    alert_sys = AlertSystem()
    
    # Configurar threshold
    alert_sys.set_threshold(AlertType.LATENCY_HIGH, 50.0)
    
    # Simular métricas
    alert_sys.check_metric(AlertType.LATENCY_HIGH, 30.0)  # OK
    alert_sys.check_metric(AlertType.LATENCY_HIGH, 80.0)  # ALERTA
    
    print(f"\nAlertas activas: {len(alert_sys.get_active_alerts())}")
    print(f"Stats: {alert_sys.get_stats()}")
