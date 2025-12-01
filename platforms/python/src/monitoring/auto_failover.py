"""
NetBoozt - Auto-Failover Manager
Cambio automático de DNS tier cuando el actual falla

By LOUST (www.loust.pro)
"""

import time
import threading
from typing import Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

try:
    from .dns_health import DNSHealthChecker, DNSHealth, DNSStatus
    from .adapter_manager import AdapterManager, DNSFallbackTier
    from ..utils.logger import log_info, log_warning, log_error
except ImportError:
    DNSHealthChecker = None
    AdapterManager = None
    DNSFallbackTier = None
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")
    def log_error(msg): print(f"[ERROR] {msg}")


@dataclass
class FailoverEvent:
    """Evento de failover"""
    timestamp: datetime
    from_tier: int
    to_tier: int
    reason: str
    success: bool


class AutoFailoverManager:
    """Gestor de failover automático de DNS - MEJORADO"""
    
    COOLDOWN_SECONDS = 30   # Reducido de 60s - cambiar más rápido
    CHECK_INTERVAL = 10     # Reducido de 15s - verificar más seguido
    MAX_FAILURES_BEFORE_SWITCH = 2  # Solo 2 fallos para cambiar (antes 3)
    
    def __init__(
        self,
        health_checker: 'DNSHealthChecker',
        adapter_manager: 'AdapterManager',
        tiers: List['DNSFallbackTier']
    ):
        self.health_checker = health_checker
        self.adapter_manager = adapter_manager
        self.tiers = tiers
        
        self.enabled = False
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        
        self.current_tier_number: Optional[int] = None
        self.last_failover: Optional[datetime] = None
        self.failover_history: List[FailoverEvent] = []
        
        self._callbacks: List[Callable[[FailoverEvent], None]] = []
    
    def enable(self):
        """Activar auto-failover"""
        self.enabled = True
        log_info("Auto-Failover ENABLED")
    
    def disable(self):
        """Desactivar auto-failover"""
        self.enabled = False
        log_info("Auto-Failover DISABLED")
    
    def on_failover(self, callback: Callable[[FailoverEvent], None]):
        """Registrar callback para eventos de failover"""
        self._callbacks.append(callback)
    
    def start(self):
        """Iniciar monitoreo de failover"""
        if self.is_running:
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._failover_loop, daemon=True)
        self._thread.start()
        log_info("Auto-Failover Manager iniciado")
    
    def stop(self):
        """Detener monitoreo"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        log_info("Auto-Failover Manager detenido")
    
    def _failover_loop(self):
        """Loop principal de verificación"""
        while self.is_running:
            try:
                if self.enabled:
                    self._check_and_failover()
                
                time.sleep(self.CHECK_INTERVAL)
                
            except Exception as e:
                log_error(f"Error en failover loop: {e}")
                time.sleep(5)
    
    def _check_and_failover(self):
        """Verificar si necesita hacer failover"""
        try:
            # Detectar tier actual
            current_tier = self._detect_current_tier()
            
            if current_tier is None:
                log_warning("No se pudo detectar tier actual")
                return
            
            self.current_tier_number = current_tier.tier
            
            # Verificar salud del tier actual
            if self._is_tier_healthy(current_tier):
                # Todo OK
                return
            
            # Tier actual está fallando
            log_warning(f"Tier {current_tier.tier} no está saludable")
            
            # Verificar cooldown
            if not self._can_failover():
                log_info("En cooldown, esperando antes de hacer failover")
                return
            
            # Buscar siguiente tier saludable
            next_tier = self._find_next_healthy_tier(current_tier.tier)
            
            if next_tier is None:
                log_error("No hay tiers saludables disponibles!")
                return
            
            # Ejecutar failover
            log_warning(f"🔄 FAILOVER: Tier {current_tier.tier} → Tier {next_tier.tier}")
            success = self._execute_failover(current_tier, next_tier)
            
            # Registrar evento
            event = FailoverEvent(
                timestamp=datetime.now(),
                from_tier=current_tier.tier,
                to_tier=next_tier.tier,
                reason="DNS tier unhealthy",
                success=success
            )
            
            self.failover_history.append(event)
            self.last_failover = datetime.now()
            
            # Notificar callbacks
            self._notify_callbacks(event)
            
        except Exception as e:
            log_error(f"Error en check_and_failover: {e}")
    
    def _detect_current_tier(self) -> Optional['DNSFallbackTier']:
        """Detectar qué tier está actualmente configurado"""
        try:
            # Obtener DNS actual del adaptador
            priority_adapter = self.adapter_manager.get_priority_adapter()
            if not priority_adapter:
                return None
            
            current_dns = priority_adapter.dns_servers
            if not current_dns:
                return None
            
            primary_dns = current_dns[0] if len(current_dns) > 0 else None
            
            # Buscar tier que coincida
            for tier in self.tiers:
                if tier.primary == primary_dns:
                    return tier
            
            # No encontrado, asumir tier 1
            return self.tiers[0] if self.tiers else None
            
        except Exception as e:
            log_error(f"Error detectando tier actual: {e}")
            return None
    
    def _is_tier_healthy(self, tier: 'DNSFallbackTier') -> bool:
        """Verificar si un tier está saludable"""
        try:
            if tier.tier == 7:  # DHCP tier
                return True  # Siempre saludable (usa DNS del router)
            
            # Verificar salud del DNS primario
            primary_health = self.health_checker.get_status(tier.primary)
            if not primary_health:
                return False
            
            # Considerar saludable si:
            # - Estado UP o SLOW
            # - Menos de 3 fallas consecutivas
            is_healthy = (
                primary_health.status in (DNSStatus.UP, DNSStatus.SLOW) and
                primary_health.consecutive_failures < 3
            )
            
            return is_healthy
            
        except Exception as e:
            log_error(f"Error verificando salud de tier: {e}")
            return False
    
    def _can_failover(self) -> bool:
        """Verificar si puede hacer failover (cooldown)"""
        if self.last_failover is None:
            return True
        
        elapsed = (datetime.now() - self.last_failover).total_seconds()
        return elapsed >= self.COOLDOWN_SECONDS
    
    def _find_next_healthy_tier(self, current_tier_number: int) -> Optional['DNSFallbackTier']:
        """Encontrar siguiente tier saludable"""
        # Ordenar tiers por número
        sorted_tiers = sorted(self.tiers, key=lambda t: t.tier)
        
        # Buscar tiers después del actual
        candidates = [t for t in sorted_tiers if t.tier > current_tier_number]
        
        # Si no hay después, buscar desde el principio
        if not candidates:
            candidates = [t for t in sorted_tiers if t.tier < current_tier_number]
        
        # Verificar cada candidato
        for tier in candidates:
            if self._is_tier_healthy(tier):
                log_info(f"Tier saludable encontrado: {tier.tier} ({tier.name})")
                return tier
        
        # Si ninguno está saludable, usar DHCP (tier 7) como último recurso
        dhcp_tier = next((t for t in self.tiers if t.tier == 7), None)
        if dhcp_tier:
            log_warning("Usando DHCP como último recurso")
            return dhcp_tier
        
        return None
    
    def _execute_failover(self, from_tier: 'DNSFallbackTier', to_tier: 'DNSFallbackTier') -> bool:
        """Ejecutar cambio de tier"""
        try:
            success = self.adapter_manager.apply_dns_tier(to_tier.tier)
            
            if success:
                log_info(f"✅ Failover exitoso: Tier {to_tier.tier}")
                return True
            else:
                log_error(f"❌ Failover falló")
                return False
                
        except Exception as e:
            log_error(f"Error ejecutando failover: {e}")
            return False
    
    def _notify_callbacks(self, event: FailoverEvent):
        """Notificar callbacks"""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                log_error(f"Error en callback de failover: {e}")
    
    def get_history(self, limit: int = 20) -> List[FailoverEvent]:
        """Obtener historial de failovers"""
        return self.failover_history[-limit:]
    
    def get_stats(self) -> dict:
        """Obtener estadísticas de failover"""
        total = len(self.failover_history)
        successful = sum(1 for e in self.failover_history if e.success)
        
        return {
            'total_failovers': total,
            'successful': successful,
            'failed': total - successful,
            'last_failover': self.last_failover,
            'enabled': self.enabled
        }


if __name__ == "__main__":
    # Test (mock)
    print("Auto-Failover Manager - Test Mode")
    print("Requiere DNSHealthChecker y AdapterManager para funcionar")
