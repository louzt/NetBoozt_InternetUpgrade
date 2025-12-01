"""
NetBoozt - Sistema de Backups Automáticos
Crea snapshots de configuración para rollback seguro

By LOUST (www.loust.pro)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import subprocess
from pathlib import Path

try:
    from ..utils.logger import log_info, log_warning, log_error
    from ..utils.notifications import get_notification_manager
except ImportError:
    def log_info(msg): print(f"[INFO] {msg}")
    def log_warning(msg): print(f"[WARN] {msg}")
    def log_error(msg): print(f"[ERROR] {msg}")
    get_notification_manager = None


@dataclass
class NetworkSnapshot:
    """Snapshot de configuración de red"""
    backup_id: str
    timestamp: datetime
    adapter_name: str
    dns_servers: List[str]
    ip_config: Dict
    tcp_settings: Dict
    registry_values: Dict
    description: str = ""
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NetworkSnapshot':
        """Crear desde diccionario"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class BackupSystem:
    """Sistema de backups de configuración"""
    
    def __init__(self, backup_dir: Path = None):
        if backup_dir is None:
            backup_dir = Path.home() / ".netboozt" / "backups"
        
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_backups = 50  # Mantener últimos 50 backups
        self.auto_backup_enabled = True
    
    def create_snapshot(self, adapter_name: str, description: str = "") -> NetworkSnapshot:
        """Crear snapshot de configuración actual"""
        try:
            backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Capturar DNS servers
            dns_servers = self._get_current_dns(adapter_name)
            
            # Capturar IP config
            ip_config = self._get_ip_config(adapter_name)
            
            # Capturar TCP settings
            tcp_settings = self._get_tcp_settings()
            
            # Capturar registry values relevantes
            registry_values = self._get_registry_values()
            
            # Crear snapshot
            snapshot = NetworkSnapshot(
                backup_id=backup_id,
                timestamp=datetime.now(),
                adapter_name=adapter_name,
                dns_servers=dns_servers,
                ip_config=ip_config,
                tcp_settings=tcp_settings,
                registry_values=registry_values,
                description=description or "Backup automático"
            )
            
            # Guardar a disco
            self._save_snapshot(snapshot)
            
            # Cleanup de backups antiguos
            self._cleanup_old_backups()
            
            # Notificación
            if get_notification_manager:
                notif = get_notification_manager()
                if notif:
                    notif.notify_backup_created(backup_id)
            
            log_info(f"Snapshot creado: {backup_id}")
            
            return snapshot
        
        except Exception as e:
            log_error(f"Error creando snapshot: {e}")
            raise
    
    def _get_current_dns(self, adapter_name: str) -> List[str]:
        """Obtener servidores DNS actuales"""
        try:
            cmd = f'Get-DnsClientServerAddress -InterfaceAlias "{adapter_name}" -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                dns_list = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                return dns_list
            
            return []
        
        except Exception as e:
            log_warning(f"Error obteniendo DNS: {e}")
            return []
    
    def _get_ip_config(self, adapter_name: str) -> Dict:
        """Obtener configuración IP"""
        try:
            cmd = f'Get-NetIPAddress -InterfaceAlias "{adapter_name}" -AddressFamily IPv4 | Select-Object IPAddress, PrefixLength | ConvertTo-Json'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            
            return {}
        
        except Exception as e:
            log_warning(f"Error obteniendo IP config: {e}")
            return {}
    
    def _get_tcp_settings(self) -> Dict:
        """Obtener configuración TCP global"""
        try:
            cmd = 'Get-NetTCPSetting -SettingName Internet | Select-Object AutoTuningLevelLocal, CongestionProvider, EcnCapability | ConvertTo-Json'
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
            
            return {}
        
        except Exception as e:
            log_warning(f"Error obteniendo TCP settings: {e}")
            return {}
    
    def _get_registry_values(self) -> Dict:
        """Obtener valores críticos del registro"""
        try:
            import winreg
            
            values = {}
            
            # Throttling Index
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                    0,
                    winreg.KEY_READ
                )
                values['NetworkThrottlingIndex'], _ = winreg.QueryValueEx(key, "NetworkThrottlingIndex")
                winreg.CloseKey(key)
            except Exception:
                pass
            
            # TCP1323Opts
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                    0,
                    winreg.KEY_READ
                )
                values['Tcp1323Opts'], _ = winreg.QueryValueEx(key, "Tcp1323Opts")
                winreg.CloseKey(key)
            except Exception:
                pass
            
            return values
        
        except Exception as e:
            log_warning(f"Error obteniendo registry: {e}")
            return {}
    
    def _save_snapshot(self, snapshot: NetworkSnapshot):
        """Guardar snapshot a disco"""
        file_path = self.backup_dir / f"backup_{snapshot.backup_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot.to_dict(), f, indent=2)
        
        log_info(f"Snapshot guardado: {file_path}")
    
    def load_snapshot(self, backup_id: str) -> Optional[NetworkSnapshot]:
        """Cargar snapshot desde disco"""
        file_path = self.backup_dir / f"backup_{backup_id}.json"
        
        if not file_path.exists():
            log_warning(f"Snapshot no encontrado: {backup_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return NetworkSnapshot.from_dict(data)
        
        except Exception as e:
            log_error(f"Error cargando snapshot: {e}")
            return None
    
    def list_snapshots(self, limit: int = 20) -> List[NetworkSnapshot]:
        """Listar snapshots disponibles"""
        snapshots = []
        
        for file_path in sorted(self.backup_dir.glob("backup_*.json"), reverse=True):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                snapshots.append(NetworkSnapshot.from_dict(data))
                
                if len(snapshots) >= limit:
                    break
            
            except Exception as e:
                log_warning(f"Error leyendo backup {file_path}: {e}")
        
        return snapshots
    
    def restore_snapshot(self, backup_id: str, adapter_name: str = None) -> bool:
        """Restaurar configuración desde snapshot"""
        snapshot = self.load_snapshot(backup_id)
        
        if not snapshot:
            return False
        
        try:
            target_adapter = adapter_name or snapshot.adapter_name
            
            # Restaurar DNS
            if snapshot.dns_servers:
                self._restore_dns(target_adapter, snapshot.dns_servers)
            
            # Restaurar registry (si es necesario)
            if snapshot.registry_values:
                self._restore_registry(snapshot.registry_values)
            
            log_info(f"Snapshot {backup_id} restaurado correctamente")
            return True
        
        except Exception as e:
            log_error(f"Error restaurando snapshot: {e}")
            return False
    
    def _restore_dns(self, adapter_name: str, dns_servers: List[str]):
        """Restaurar servidores DNS"""
        try:
            # Limpiar DNS actual
            subprocess.run(
                ["powershell", "-Command", f'Set-DnsClientServerAddress -InterfaceAlias "{adapter_name}" -ResetServerAddresses'],
                timeout=5,
                check=True
            )
            
            # Aplicar DNS del backup
            if dns_servers:
                dns_str = ','.join(dns_servers)
                subprocess.run(
                    ["powershell", "-Command", f'Set-DnsClientServerAddress -InterfaceAlias "{adapter_name}" -ServerAddresses {dns_str}'],
                    timeout=5,
                    check=True
                )
            
            log_info(f"DNS restaurado: {dns_servers}")
        
        except Exception as e:
            log_error(f"Error restaurando DNS: {e}")
            raise
    
    def _restore_registry(self, registry_values: Dict):
        """Restaurar valores del registro"""
        try:
            import winreg
            
            # NetworkThrottlingIndex
            if 'NetworkThrottlingIndex' in registry_values:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                    0,
                    winreg.KEY_WRITE
                )
                winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, registry_values['NetworkThrottlingIndex'])
                winreg.CloseKey(key)
            
            # Tcp1323Opts
            if 'Tcp1323Opts' in registry_values:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                    0,
                    winreg.KEY_WRITE
                )
                winreg.SetValueEx(key, "Tcp1323Opts", 0, winreg.REG_DWORD, registry_values['Tcp1323Opts'])
                winreg.CloseKey(key)
            
            log_info("Registry restaurado")
        
        except Exception as e:
            log_warning(f"Error restaurando registry: {e}")
    
    def delete_snapshot(self, backup_id: str) -> bool:
        """Eliminar snapshot"""
        file_path = self.backup_dir / f"backup_{backup_id}.json"
        
        if file_path.exists():
            file_path.unlink()
            log_info(f"Snapshot eliminado: {backup_id}")
            return True
        
        return False
    
    def _cleanup_old_backups(self):
        """Eliminar backups antiguos"""
        snapshots = list(self.backup_dir.glob("backup_*.json"))
        
        if len(snapshots) > self.max_backups:
            # Ordenar por fecha (más antiguos primero)
            snapshots.sort(key=lambda p: p.stat().st_mtime)
            
            # Eliminar los más antiguos
            to_delete = snapshots[:len(snapshots) - self.max_backups]
            
            for file_path in to_delete:
                file_path.unlink()
                log_info(f"Backup antiguo eliminado: {file_path.name}")


# Singleton global
_backup_system: Optional[BackupSystem] = None


def get_backup_system() -> BackupSystem:
    """Obtener instancia global del sistema de backups"""
    global _backup_system
    
    if _backup_system is None:
        _backup_system = BackupSystem()
    
    return _backup_system


if __name__ == "__main__":
    # Test
    backup_sys = BackupSystem()
    
    # Crear snapshot
    snapshot = backup_sys.create_snapshot("Ethernet", "Test backup")
    print(f"Snapshot creado: {snapshot.backup_id}")
    
    # Listar
    snapshots = backup_sys.list_snapshots()
    print(f"\nSnapshots disponibles: {len(snapshots)}")
