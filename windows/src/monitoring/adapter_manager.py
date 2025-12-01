"""
NetBoozt - Adapter Manager
Gestión avanzada de adaptadores de red con detección de prioridades y DNS fallback

By LOUST (www.loust.pro)
"""

import subprocess
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Importar logger para debugging
try:
    from ..utils.logger import log_info, log_warning, log_error
except ImportError:
    # Fallback si no hay logger
    def log_info(msg, *args): print(f"[INFO] {msg}")
    def log_warning(msg, *args): print(f"[WARN] {msg}")
    def log_error(msg, *args): print(f"[ERROR] {msg}")


class AdapterStatus(Enum):
    """Estados de adaptador"""
    UP = "Up"
    DOWN = "Down"
    DISCONNECTED = "Disconnected"
    DISABLED = "Disabled"


class DNSProvider(Enum):
    """Proveedores DNS conocidos"""
    CLOUDFLARE = ("1.1.1.1", "1.0.0.1")
    CLOUDFLARE_FAMILY = ("1.1.1.3", "1.0.0.3")
    GOOGLE = ("8.8.8.8", "8.8.4.4")
    QUAD9 = ("9.9.9.9", "149.112.112.112")
    OPENDNS = ("208.67.222.222", "208.67.220.220")
    OPENDNS_FAMILY = ("208.67.222.123", "208.67.220.123")
    ADGUARD = ("94.140.14.14", "94.140.15.15")
    ADGUARD_FAMILY = ("94.140.14.15", "94.140.15.16")
    CLEANBROWSING = ("185.228.168.9", "185.228.169.9")
    CLEANBROWSING_FAMILY = ("185.228.168.168", "185.228.169.168")
    LEVEL3 = ("209.244.0.3", "209.244.0.4")
    VERISIGN = ("64.6.64.6", "64.6.65.6")


@dataclass
class NetworkAdapter:
    """Información de adaptador de red"""
    name: str
    interface_description: str
    status: AdapterStatus
    metric: int
    mac_address: str
    speed_mbps: int
    mtu: int
    dns_servers: List[str]
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    default_gateway: Optional[str] = None
    dhcp_enabled: bool = True
    
    @property
    def is_active(self) -> bool:
        """Verificar si el adaptador está activo"""
        return self.status == AdapterStatus.UP
    
    @property
    def dns_provider(self) -> Optional[str]:
        """Identificar proveedor DNS"""
        if not self.dns_servers:
            return "DHCP/Router"
        
        first_dns = self.dns_servers[0]
        
        for provider in DNSProvider:
            if first_dns in provider.value:
                return provider.name.replace('_', ' ').title()
        
        return "Custom"
    
    @property
    def priority_rank(self) -> int:
        """Ranking de prioridad (métrica más baja = mayor prioridad)"""
        return self.metric


@dataclass
class DNSFallbackTier:
    """Nivel de DNS fallback"""
    tier: int
    provider: str
    primary: str
    secondary: str
    active: bool = False
    latency_ms: Optional[float] = None


class AdapterManager:
    """Gestor de adaptadores de red"""
    
    # DNS Fallback tiers (7 niveles)
    DNS_FALLBACK_TIERS = [
        DNSFallbackTier(1, "Cloudflare", "1.1.1.1", "1.0.0.1"),
        DNSFallbackTier(2, "Google", "8.8.8.8", "8.8.4.4"),
        DNSFallbackTier(3, "Quad9", "9.9.9.9", "149.112.112.112"),
        DNSFallbackTier(4, "OpenDNS", "208.67.222.222", "208.67.220.220"),
        DNSFallbackTier(5, "AdGuard", "94.140.14.14", "94.140.15.15"),
        DNSFallbackTier(6, "CleanBrowsing", "185.228.168.9", "185.228.169.9"),
        DNSFallbackTier(7, "Router DHCP", "Auto", "Auto"),
    ]
    
    def __init__(self):
        self.adapters: List[NetworkAdapter] = []
        self._detect_adapters()
    
    def _run_powershell(self, command: str) -> str:
        """Ejecutar comando PowerShell sin ventana visible"""
        try:
            log_info(f"Executing PowerShell command: {command[:100]}...")
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            log_info(f"PowerShell stdout length: {len(result.stdout)}")
            if result.stderr:
                log_warning(f"PowerShell stderr: {result.stderr}")
            return result.stdout.strip()
        except Exception as e:
            log_error(f"Error ejecutando PowerShell: {e}")
            return ""
    
    def _detect_adapters(self):
        """Detectar todos los adaptadores de red"""
        log_info("Starting adapter detection...")
        
        # Obtener adaptadores con Get-NetAdapter
        cmd = """
        Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, 
            MacAddress, LinkSpeed, InterfaceMetric | ConvertTo-Json
        """
        output = self._run_powershell(cmd)
        
        if not output:
            log_warning("No output from Get-NetAdapter command")
            return
        
        try:
            import json
            adapters_data = json.loads(output)
            log_info(f"Parsed {len(adapters_data) if isinstance(adapters_data, list) else 1} adapter(s)")
            
            # Asegurar que sea lista
            if isinstance(adapters_data, dict):
                adapters_data = [adapters_data]
            
            for data in adapters_data:
                log_info(f"Processing adapter: {data.get('Name', 'Unknown')}")
                
                # Obtener configuración IP
                ip_config = self._get_adapter_ip_config(data['Name'])
                
                # Parsear velocidad
                speed_str = data.get('LinkSpeed', '0 Mbps')
                speed_match = re.search(r'(\d+(?:\.\d+)?)\s*([GM]?bps)', speed_str)
                if speed_match:
                    value = float(speed_match.group(1))
                    unit = speed_match.group(2)
                    if unit == 'Gbps':
                        speed_mbps = int(value * 1000)
                    else:
                        speed_mbps = int(value)
                else:
                    speed_mbps = 1000
                
                # Crear adaptador
                # Fix: Asegurar que InterfaceMetric no sea None
                metric_value = data.get('InterfaceMetric', 100)
                if metric_value is None:
                    metric_value = 100
                    
                adapter = NetworkAdapter(
                    name=data['Name'],
                    interface_description=data.get('InterfaceDescription', ''),
                    status=AdapterStatus(data.get('Status', 'Down')),
                    metric=int(metric_value),
                    mac_address=data.get('MacAddress', ''),
                    speed_mbps=speed_mbps,
                    mtu=ip_config.get('mtu', 1500),
                    dns_servers=ip_config.get('dns', []),
                    ipv4_address=ip_config.get('ipv4'),
                    ipv6_address=ip_config.get('ipv6'),
                    default_gateway=ip_config.get('gateway'),
                    dhcp_enabled=ip_config.get('dhcp', True)
                )
                
                self.adapters.append(adapter)
                log_info(f"✓ Added adapter: {adapter.name} (Metric: {adapter.metric}, Speed: {adapter.speed_mbps} Mbps)")
        
        except Exception as e:
            log_error(f"Error parseando adaptadores: {e}", e)
    
    def _get_adapter_ip_config(self, adapter_name: str) -> Dict:
        """Obtener configuración IP de un adaptador"""
        cmd = f"""
        $adapter = Get-NetIPConfiguration -InterfaceAlias '{adapter_name}' -ErrorAction SilentlyContinue
        if ($adapter) {{
            @{{
                ipv4 = ($adapter.IPv4Address.IPAddress | Select-Object -First 1)
                ipv6 = ($adapter.IPv6Address.IPAddress | Select-Object -First 1)
                gateway = ($adapter.IPv4DefaultGateway.NextHop | Select-Object -First 1)
                dns = @(Get-DnsClientServerAddress -InterfaceAlias '{adapter_name}' -AddressFamily IPv4 | 
                    Select-Object -ExpandProperty ServerAddresses)
                dhcp = (Get-NetIPInterface -InterfaceAlias '{adapter_name}' -AddressFamily IPv4 | 
                    Select-Object -ExpandProperty Dhcp) -eq 'Enabled'
            }} | ConvertTo-Json
        }}
        """
        output = self._run_powershell(cmd)
        
        if not output:
            return {'mtu': 1500, 'dns': [], 'dhcp': True}
        
        try:
            import json
            data = json.loads(output)
            
            # Parsear DNS (puede ser string único o array)
            dns_raw = data.get('dns', [])
            if isinstance(dns_raw, str):
                dns_list = [dns_raw] if dns_raw else []
            else:
                dns_list = dns_raw if dns_raw else []
            
            return {
                'ipv4': data.get('ipv4'),
                'ipv6': data.get('ipv6'),
                'gateway': data.get('gateway'),
                'dns': dns_list,
                'dhcp': data.get('dhcp', True),
                'mtu': 1500  # TODO: Obtener MTU real
            }
        except Exception:
            # PowerShell parsing error
            return {'mtu': 1500, 'dns': [], 'dhcp': True}
    
    def get_active_adapters(self) -> List[NetworkAdapter]:
        """Obtener adaptadores activos"""
        return [a for a in self.adapters if a.is_active]
    
    def get_adapter_by_name(self, name: str) -> Optional[NetworkAdapter]:
        """Obtener adaptador por nombre"""
        for adapter in self.adapters:
            if adapter.name.lower() == name.lower():
                return adapter
        return None
    
    def get_priority_adapter(self) -> Optional[NetworkAdapter]:
        """Obtener adaptador con mayor prioridad (métrica más baja)"""
        active = self.get_active_adapters()
        if not active:
            return None
        
        return min(active, key=lambda a: a.metric)
    
    def get_adapters_sorted_by_priority(self) -> List[NetworkAdapter]:
        """Obtener adaptadores ordenados por prioridad"""
        return sorted(self.adapters, key=lambda a: a.metric)
    
    def detect_active_dns_tier(self) -> Optional[DNSFallbackTier]:
        """Detectar qué tier de DNS está activo actualmente"""
        priority_adapter = self.get_priority_adapter()
        
        if not priority_adapter or not priority_adapter.dns_servers:
            return self.DNS_FALLBACK_TIERS[-1]  # DHCP/Router
        
        primary_dns = priority_adapter.dns_servers[0]
        
        # Buscar en tiers
        for tier in self.DNS_FALLBACK_TIERS[:-1]:  # Excluir DHCP
            if primary_dns == tier.primary:
                tier.active = True
                return tier
        
        # Si no coincide con ningún tier, crear custom
        return DNSFallbackTier(
            tier=0,
            provider="Custom",
            primary=primary_dns,
            secondary=priority_adapter.dns_servers[1] if len(priority_adapter.dns_servers) > 1 else "",
            active=True
        )
    
    def get_dns_fallback_status(self) -> List[DNSFallbackTier]:
        """Obtener estado de todos los tiers con marcado del activo"""
        active_tier = self.detect_active_dns_tier()
        
        tiers = self.DNS_FALLBACK_TIERS.copy()
        for tier in tiers:
            tier.active = (active_tier and tier.tier == active_tier.tier)
        
        return tiers
    
    def set_adapter_metric(self, adapter_name: str, metric: int) -> bool:
        """Cambiar métrica de un adaptador"""
        cmd = f"""
        Set-NetIPInterface -InterfaceAlias '{adapter_name}' -InterfaceMetric {metric}
        """
        try:
            self._run_powershell(cmd)
            # Redetectar
            self._detect_adapters()
            return True
        except Exception:
            # PowerShell command failed
            return False
    
    def set_dns_servers(self, adapter_name: str, dns_servers: List[str]) -> bool:
        """Configurar servidores DNS de un adaptador"""
        dns_list = ",".join([f"'{dns}'" for dns in dns_servers])
        
        cmd = f"""
        Set-DnsClientServerAddress -InterfaceAlias '{adapter_name}' -ServerAddresses {dns_list}
        """
        try:
            self._run_powershell(cmd)
            # Redetectar
            self._detect_adapters()
            return True
        except Exception:
            # PowerShell command failed
            return False
    
    def apply_dns_tier(self, tier_number: int) -> bool:
        """Aplicar un tier de DNS al adaptador prioritario"""
        if tier_number < 1 or tier_number > len(self.DNS_FALLBACK_TIERS):
            return False
        
        priority_adapter = self.get_priority_adapter()
        if not priority_adapter:
            return False
        
        tier = self.DNS_FALLBACK_TIERS[tier_number - 1]
        
        if tier.tier == 7:  # DHCP
            # Configurar DHCP
            cmd = f"""
            Set-DnsClientServerAddress -InterfaceAlias '{priority_adapter.name}' -ResetServerAddresses
            """
            try:
                self._run_powershell(cmd)
                self._detect_adapters()
                return True
            except Exception:
                # PowerShell command failed
                return False
        else:
            # Configurar DNS estático
            return self.set_dns_servers(
                priority_adapter.name,
                [tier.primary, tier.secondary]
            )
    
    def get_adapter_summary(self) -> Dict:
        """Resumen de adaptadores"""
        active = self.get_active_adapters()
        priority = self.get_priority_adapter()
        
        return {
            'total_adapters': len(self.adapters),
            'active_adapters': len(active),
            'priority_adapter': priority.name if priority else None,
            'priority_metric': priority.metric if priority else None,
            'dns_provider': priority.dns_provider if priority else None,
            'active_dns_tier': self.detect_active_dns_tier()
        }


# Singleton
_adapter_manager_instance = None

def get_adapter_manager() -> AdapterManager:
    """Obtener instancia única del adapter manager"""
    global _adapter_manager_instance
    if _adapter_manager_instance is None:
        _adapter_manager_instance = AdapterManager()
    return _adapter_manager_instance
