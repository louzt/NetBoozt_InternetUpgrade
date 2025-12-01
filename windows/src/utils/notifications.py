"""
NetBoozt - Windows Notifications
Sistema de notificaciones desktop para Windows

By LOUST (www.loust.pro)
"""

import sys
from typing import Optional

try:
    from winotify import Notification, audio
    WINOTIFY_AVAILABLE = True
except ImportError:
    WINOTIFY_AVAILABLE = False
    print("[WARN] winotify no disponible. Instalar con: pip install winotify")

try:
    from ..utils.logger import log_info, log_warning
except ImportError:
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")


class NotificationManager:
    """Gestor de notificaciones desktop de Windows"""
    
    def __init__(self, app_name: str = "NetBoozt", app_id: str = "NetBoozt.NetworkOptimizer"):
        self.app_name = app_name
        self.app_id = app_id
        self.enabled = True
        
        if not WINOTIFY_AVAILABLE:
            log_warning("winotify no disponible - notificaciones deshabilitadas")
            self.enabled = False
    
    def show(
        self,
        title: str,
        message: str,
        duration: str = "short",
        icon: Optional[str] = None,
        sound: bool = True
    ) -> bool:
        """
        Mostrar notificación de Windows
        
        Args:
            title: Título de la notificación
            message: Mensaje
            duration: "short" (5s) o "long" (25s)
            icon: Ruta a icono (opcional)
            sound: Reproducir sonido
            
        Returns:
            True si se mostró, False si falló
        """
        if not self.enabled:
            # Fallback a print
            print(f"[NOTIFICATION] {title}: {message}")
            return False
        
        try:
            toast = Notification(
                app_id=self.app_id,
                title=title,
                msg=message,
                duration=duration,
                icon=icon
            )
            
            # Sonido
            if sound:
                toast.set_audio(audio.Default, loop=False)
            else:
                toast.set_audio(audio.Silent, loop=False)
            
            # Mostrar
            toast.show()
            log_info(f"Notificación mostrada: {title}")
            return True
            
        except Exception as e:
            log_warning(f"Error mostrando notificación: {e}")
            return False
    
    def notify_dns_failover(self, from_tier: int, to_tier: int, tier_name: str):
        """Notificación específica de DNS failover"""
        title = "🔄 DNS Failover Ejecutado"
        message = f"Cambiado de Tier {from_tier} a Tier {to_tier}\n{tier_name}"
        
        self.show(title, message, duration="long", sound=True)
    
    def notify_optimization_applied(self, count: int, reboot_required: bool = False):
        """Notificación de optimizaciones aplicadas"""
        title = "✅ Optimizaciones Aplicadas"
        message = f"{count} optimizaciones activadas correctamente"
        
        if reboot_required:
            message += "\n\n⚠️ Reinicio requerido para algunos cambios"
        
        self.show(title, message, duration="short", sound=False)
    
    def notify_alert(self, alert_type: str, details: str):
        """Notificación de alerta"""
        icons = {
            'latency_high': '⚠️',
            'speed_drop': '📉',
            'packet_loss': '📦',
            'dns_down': '🔴'
        }
        
        icon_emoji = icons.get(alert_type, '⚠️')
        title = f"{icon_emoji} Alerta de Red"
        
        self.show(title, details, duration="long", sound=True)
    
    def notify_backup_created(self, backup_id: str):
        """Notificación de backup creado"""
        title = "💾 Backup Creado"
        message = f"Snapshot de configuración guardado\nID: {backup_id}"
        
        self.show(title, message, duration="short", sound=False)
    
    def notify_error(self, error_title: str, error_msg: str):
        """Notificación de error"""
        title = f"❌ {error_title}"
        
        self.show(title, error_msg, duration="long", sound=True)
    
    def disable(self):
        """Desactivar notificaciones"""
        self.enabled = False
        log_info("Notificaciones deshabilitadas")
    
    def enable(self):
        """Activar notificaciones"""
        if WINOTIFY_AVAILABLE:
            self.enabled = True
            log_info("Notificaciones habilitadas")
        else:
            log_warning("winotify no disponible - no se pueden habilitar notificaciones")


# Singleton global
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Obtener instancia global del notification manager"""
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    
    return _notification_manager


if __name__ == "__main__":
    # Test
    nm = NotificationManager()
    
    print("Test de notificaciones...")
    
    # Test básico
    nm.show(
        "Test NetBoozt",
        "Esta es una notificación de prueba",
        duration="short"
    )
    
    # Test failover
    import time
    time.sleep(2)
    nm.notify_dns_failover(1, 2, "Cloudflare DNS")
    
    # Test alerta
    time.sleep(2)
    nm.notify_alert("latency_high", "Latencia alta detectada: 250ms")
    
    print("Tests enviados. Verifica las notificaciones de Windows.")
