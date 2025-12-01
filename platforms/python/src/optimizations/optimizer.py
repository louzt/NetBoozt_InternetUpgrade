"""
NetBoozt - Sistema de Aplicación de Optimizaciones
Ejecuta cambios reales en el sistema (PowerShell + Registry)

By LOUST (www.loust.pro)
"""

import subprocess
import winreg
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from ..utils.logger import log_info, log_error, log_warning
except ImportError:
    def log_info(msg, *args): print(f"[INFO] {msg}")
    def log_error(msg, *args): print(f"[ERROR] {msg}")
    def log_warning(msg, *args): print(f"[WARN] {msg}")


class OptimizationResult(Enum):
    """Resultado de aplicar optimización"""
    SUCCESS = "success"
    FAILED = "failed"
    ALREADY_SET = "already_set"
    REQUIRES_REBOOT = "requires_reboot"


@dataclass
class ApplyResult:
    """Resultado de aplicación"""
    optimization: str
    result: OptimizationResult
    message: str
    requires_reboot: bool = False


class NetworkOptimizer:
    """Aplicador de optimizaciones de red"""
    
    TCP_PARAMS = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
    INTERFACE_PARAMS = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    
    def __init__(self):
        self.results = []
        self.reboot_required = False
    
    def _run_powershell(self, command: str, timeout: int = 10) -> Tuple[bool, str]:
        """Ejecutar comando PowerShell"""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            return success, output.strip()
            
        except subprocess.TimeoutExpired:
            log_error(f"PowerShell timeout: {command[:50]}...")
            return False, "Timeout"
        except Exception as e:
            log_error(f"PowerShell error: {e}")
            return False, str(e)
    
    def _set_registry_dword(self, path: str, key: str, value: int) -> bool:
        """Establecer valor DWORD en registro"""
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg, key, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(reg)
            log_info(f"Registry set: {path}\\{key} = {value}")
            return True
        except Exception as e:
            log_error(f"Registry error: {e}")
            return False
    
    def _get_registry_dword(self, path: str, key: str) -> Optional[int]:
        """Leer valor DWORD del registro"""
        try:
            reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(reg, key)
            winreg.CloseKey(reg)
            return value
        except Exception:
            return None
    
    # ==================== TCP OPTIMIZATIONS ====================
    
    def apply_tcp_congestion_control(self, enable: bool = True) -> ApplyResult:
        """Activar TCP Congestion Control (CTCP/Compound)"""
        try:
            # Windows usa "ctcp" para Compound TCP
            cmd = "Set-NetTCPSetting -SettingName Internet -CongestionProvider ctcp" if enable else \
                  "Set-NetTCPSetting -SettingName Internet -CongestionProvider default"
            
            success, output = self._run_powershell(cmd)
            
            if success:
                return ApplyResult(
                    optimization="tcp_congestion",
                    result=OptimizationResult.SUCCESS,
                    message=f"TCP Congestion Control {'activado' if enable else 'desactivado'}",
                    requires_reboot=False
                )
            else:
                return ApplyResult(
                    optimization="tcp_congestion",
                    result=OptimizationResult.FAILED,
                    message=f"Error: {output}"
                )
        except Exception as e:
            return ApplyResult(
                optimization="tcp_congestion",
                result=OptimizationResult.FAILED,
                message=str(e)
            )
    
    def apply_ecn(self, enable: bool = True) -> ApplyResult:
        """Activar ECN (Explicit Congestion Notification)"""
        try:
            # 0=disabled, 1=enabled
            cmd = f"Set-NetTCPSetting -SettingName Internet -EcnCapability {'Enabled' if enable else 'Disabled'}"
            success, output = self._run_powershell(cmd)
            
            if success:
                return ApplyResult(
                    optimization="ecn",
                    result=OptimizationResult.SUCCESS,
                    message=f"ECN {'activado' if enable else 'desactivado'}"
                )
            else:
                return ApplyResult(
                    optimization="ecn",
                    result=OptimizationResult.FAILED,
                    message=f"Error: {output}"
                )
        except Exception as e:
            return ApplyResult("ecn", OptimizationResult.FAILED, str(e))
    
    def apply_rss(self, enable: bool = True) -> ApplyResult:
        """Activar RSS (Receive Side Scaling)"""
        try:
            # Obtener adaptador principal
            cmd_get = "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -First 1 -ExpandProperty Name"
            success, adapter_name = self._run_powershell(cmd_get)
            
            if not success or not adapter_name:
                return ApplyResult("rss", OptimizationResult.FAILED, "No se pudo detectar adaptador")
            
            # Habilitar/Deshabilitar RSS
            state = "Enabled" if enable else "Disabled"
            cmd = f"Set-NetAdapterRss -Name '{adapter_name}' -Enabled ${enable}"
            success, output = self._run_powershell(cmd)
            
            if success:
                return ApplyResult(
                    optimization="rss",
                    result=OptimizationResult.SUCCESS,
                    message=f"RSS {state} en {adapter_name}"
                )
            else:
                return ApplyResult("rss", OptimizationResult.FAILED, f"Error: {output}")
        except Exception as e:
            return ApplyResult("rss", OptimizationResult.FAILED, str(e))
    
    def apply_window_scaling(self, enable: bool = True) -> ApplyResult:
        """Activar TCP Window Scaling"""
        try:
            # 0=disabled, 1=enabled (default), 2=highly restricted, 3=restricted
            value = 1 if enable else 0
            success = self._set_registry_dword(self.TCP_PARAMS, "Tcp1323Opts", value)
            
            if success:
                return ApplyResult(
                    optimization="window_scaling",
                    result=OptimizationResult.SUCCESS,
                    message=f"Window Scaling {'activado' if enable else 'desactivado'}",
                    requires_reboot=True
                )
            else:
                return ApplyResult("window_scaling", OptimizationResult.FAILED, "Error en registro")
        except Exception as e:
            return ApplyResult("window_scaling", OptimizationResult.FAILED, str(e))
    
    def apply_tcp_timestamps(self, enable: bool = True) -> ApplyResult:
        """Activar TCP Timestamps"""
        try:
            # Incluido en Tcp1323Opts (bit 0 = timestamps, bit 1 = window scaling)
            current = self._get_registry_dword(self.TCP_PARAMS, "Tcp1323Opts") or 0
            
            if enable:
                # Set bit 0 (timestamps)
                new_value = current | 1
            else:
                # Clear bit 0
                new_value = current & ~1
            
            success = self._set_registry_dword(self.TCP_PARAMS, "Tcp1323Opts", new_value)
            
            if success:
                return ApplyResult(
                    optimization="tcp_timestamps",
                    result=OptimizationResult.SUCCESS,
                    message=f"TCP Timestamps {'activados' if enable else 'desactivados'}",
                    requires_reboot=True
                )
            else:
                return ApplyResult("tcp_timestamps", OptimizationResult.FAILED, "Error en registro")
        except Exception as e:
            return ApplyResult("tcp_timestamps", OptimizationResult.FAILED, str(e))
    
    def apply_chimney_offload(self, enable: bool = False) -> ApplyResult:
        """Activar Chimney Offload (EXPERIMENTAL - puede causar problemas)"""
        try:
            # Chimney es experimental y puede causar issues
            state = "enabled" if enable else "disabled"
            cmd = f"netsh int tcp set global chimney={state}"
            success, output = self._run_powershell(cmd)
            
            if success:
                return ApplyResult(
                    optimization="chimney_offload",
                    result=OptimizationResult.SUCCESS,
                    message=f"Chimney Offload {state} (EXPERIMENTAL)",
                    requires_reboot=True
                )
            else:
                return ApplyResult("chimney_offload", OptimizationResult.FAILED, f"Error: {output}")
        except Exception as e:
            return ApplyResult("chimney_offload", OptimizationResult.FAILED, str(e))
    
    def apply_network_throttling(self, disable: bool = True) -> ApplyResult:
        """Desactivar Network Throttling Index (10ms delay artificial)"""
        try:
            # NetworkThrottlingIndex: FFFFFFFF = disabled, 10 = enabled (default)
            value = 0xFFFFFFFF if disable else 10
            
            path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
            success = self._set_registry_dword(path, "NetworkThrottlingIndex", value)
            
            if success:
                return ApplyResult(
                    optimization="network_throttling",
                    result=OptimizationResult.SUCCESS,
                    message=f"Network Throttling {'desactivado' if disable else 'activado'}",
                    requires_reboot=True
                )
            else:
                return ApplyResult("network_throttling", OptimizationResult.FAILED, "Error en registro")
        except Exception as e:
            return ApplyResult("network_throttling", OptimizationResult.FAILED, str(e))
    
    def apply_auto_tuning(self, enable: bool = True) -> ApplyResult:
        """Activar Auto-Tuning Level"""
        try:
            # normal, highlyrestricted, restricted, experimental, disabled
            level = "normal" if enable else "disabled"
            cmd = f"netsh interface tcp set global autotuninglevel={level}"
            success, output = self._run_powershell(cmd)
            
            if success:
                return ApplyResult(
                    optimization="auto_tuning",
                    result=OptimizationResult.SUCCESS,
                    message=f"Auto-Tuning Level = {level}"
                )
            else:
                return ApplyResult("auto_tuning", OptimizationResult.FAILED, f"Error: {output}")
        except Exception as e:
            return ApplyResult("auto_tuning", OptimizationResult.FAILED, str(e))
    
    # ==================== APLICAR MÚLTIPLES ====================
    
    def apply_optimization(self, key: str, enable: bool) -> ApplyResult:
        """Aplicar una optimización específica"""
        mapping = {
            'hystart': self.apply_tcp_congestion_control,
            'ecn': self.apply_ecn,
            'rss_enabled': self.apply_rss,
            'window_scaling': self.apply_window_scaling,
            'timestamps': self.apply_tcp_timestamps,
            'chimney': self.apply_chimney_offload,
            'throttling_disabled': self.apply_network_throttling,
            'auto_tuning': self.apply_auto_tuning,
        }
        
        if key in mapping:
            log_info(f"Aplicando {key}: {'ON' if enable else 'OFF'}")
            result = mapping[key](enable)
            self.results.append(result)
            
            if result.requires_reboot:
                self.reboot_required = True
            
            return result
        else:
            log_warning(f"Optimización no implementada: {key}")
            return ApplyResult(
                optimization=key,
                result=OptimizationResult.FAILED,
                message=f"Optimización '{key}' no implementada aún"
            )
    
    def apply_batch(self, optimizations: Dict[str, bool]) -> Dict[str, ApplyResult]:
        """Aplicar múltiples optimizaciones"""
        results = {}
        
        for key, enable in optimizations.items():
            result = self.apply_optimization(key, enable)
            results[key] = result
        
        return results
    
    def get_summary(self) -> Dict:
        """Resumen de resultados"""
        success = sum(1 for r in self.results if r.result == OptimizationResult.SUCCESS)
        failed = sum(1 for r in self.results if r.result == OptimizationResult.FAILED)
        
        return {
            'total': len(self.results),
            'success': success,
            'failed': failed,
            'reboot_required': self.reboot_required,
            'results': self.results
        }


if __name__ == "__main__":
    # Test
    optimizer = NetworkOptimizer()
    
    # Probar una optimización
    result = optimizer.apply_ecn(True)
    log_info(f"Resultado: {result.result.value} - {result.message}")
    
    summary = optimizer.get_summary()
    log_info(f"Summary: {summary['success']}/{summary['total']} exitosas")
    if summary['reboot_required']:
        log_warning("⚠️ Se requiere reinicio para que algunos cambios tengan efecto")
