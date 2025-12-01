"""
NetBoozt - Detección de Optimizaciones Activas
Lee el registro de Windows para determinar qué optimizaciones están aplicadas

By LOUST (www.loust.pro)
"""

import winreg
import subprocess
import re
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class OptimizationState:
    """Estado de una optimización"""
    name: str
    enabled: bool
    current_value: Any
    recommended_value: Any
    registry_path: Optional[str] = None
    registry_key: Optional[str] = None


class OptimizationDetector:
    """Detector de optimizaciones de red en Windows"""
    
    # Rutas del registro
    TCP_PARAMS = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
    AFD_PARAMS = r"SYSTEM\CurrentControlSet\Services\AFD\Parameters"
    NDIS_PARAMS = r"SYSTEM\CurrentControlSet\Services\NDIS\Parameters"
    
    def __init__(self):
        self.detected_states: Dict[str, OptimizationState] = {}
    
    def detect_all(self) -> Dict[str, OptimizationState]:
        """
        Detectar el estado de todas las optimizaciones
        
        Returns:
            Dict con estado de cada optimización
        """
        self.detected_states = {}
        
        # TCP Congestion Control
        self._detect_tcp_congestion_control()
        
        # RSS (Receive Side Scaling)
        self._detect_rss()
        
        # ECN (Explicit Congestion Notification)
        self._detect_ecn()
        
        # TCP Fast Open
        self._detect_tcp_fast_open()
        
        # Window Scaling
        self._detect_window_scaling()
        
        # Timestamps
        self._detect_timestamps()
        
        # SACK (Selective Acknowledgment)
        self._detect_sack()
        
        # Chimney Offload
        self._detect_chimney_offload()
        
        # Network Throttling Index
        self._detect_network_throttling()
        
        # Task Offload
        self._detect_task_offload()
        
        # Nagle Algorithm
        self._detect_nagle()
        
        # Auto Tuning Level
        self._detect_auto_tuning()
        
        # DCA (Direct Cache Access)
        self._detect_dca()
        
        return self.detected_states
    
    def _read_registry_dword(self, path: str, key: str) -> Optional[int]:
        """Leer valor DWORD del registro"""
        try:
            reg_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                path,
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(reg_key, key)
            winreg.CloseKey(reg_key)
            return value
        except (FileNotFoundError, OSError):
            return None
    
    def _run_netsh_command(self, command: str) -> str:
        """Ejecutar comando netsh sin ventana visible"""
        try:
            result = subprocess.run(
                f"netsh {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            return result.stdout
        except Exception as e:
            # Silently ignore netsh errors (puede no estar disponible)
            return ""
    
    def _detect_tcp_congestion_control(self):
        """Detectar algoritmo de control de congestión TCP"""
        output = self._run_netsh_command("interface tcp show global")
        
        # Buscar "Congestion Provider" en el output
        match = re.search(r"Congestion Provider\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            provider = match.group(1).lower()
            enabled = provider in ["ctcp", "cubic", "bbr"]
        else:
            # Si no está en netsh, revisar registro
            value = self._read_registry_dword(self.TCP_PARAMS, "TcpCongestionControl")
            enabled = value == 1 if value is not None else False
            provider = "ctcp" if enabled else "compound"
        
        self.detected_states["tcp_congestion"] = OptimizationState(
            name="TCP Congestion Control",
            enabled=enabled,
            current_value=provider,
            recommended_value="ctcp",
            registry_path=self.TCP_PARAMS,
            registry_key="TcpCongestionControl"
        )
    
    def _detect_rss(self):
        """Detectar RSS (Receive Side Scaling)"""
        output = self._run_netsh_command("interface tcp show global")
        
        match = re.search(r"Receive-Side Scaling State\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            state = match.group(1).lower()
            enabled = state == "enabled"
        else:
            # Fallback: revisar registro
            value = self._read_registry_dword(self.NDIS_PARAMS, "RssBaseCpu")
            enabled = value is not None
        
        self.detected_states["rss"] = OptimizationState(
            name="Receive Side Scaling",
            enabled=enabled,
            current_value="enabled" if enabled else "disabled",
            recommended_value="enabled"
        )
    
    def _detect_ecn(self):
        """Detectar ECN (Explicit Congestion Notification)"""
        output = self._run_netsh_command("interface tcp show global")
        
        match = re.search(r"ECN Capability\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            capability = match.group(1).lower()
            enabled = capability == "enabled"
        else:
            value = self._read_registry_dword(self.TCP_PARAMS, "EnableECN")
            enabled = value == 1 if value is not None else False
        
        self.detected_states["ecn"] = OptimizationState(
            name="ECN (Explicit Congestion Notification)",
            enabled=enabled,
            current_value="enabled" if enabled else "disabled",
            recommended_value="enabled",
            registry_path=self.TCP_PARAMS,
            registry_key="EnableECN"
        )
    
    def _detect_tcp_fast_open(self):
        """Detectar TCP Fast Open"""
        # TCP Fast Open es nuevo en Windows Server 2016+/Windows 10 1607+
        value = self._read_registry_dword(self.TCP_PARAMS, "TcpFastOpen")
        enabled = value == 1 if value is not None else False
        
        self.detected_states["tcp_fast_open"] = OptimizationState(
            name="TCP Fast Open",
            enabled=enabled,
            current_value=value,
            recommended_value=1,
            registry_path=self.TCP_PARAMS,
            registry_key="TcpFastOpen"
        )
    
    def _detect_window_scaling(self):
        """Detectar Window Scaling"""
        output = self._run_netsh_command("interface tcp show global")
        
        match = re.search(r"Receive Window Auto-Tuning Level\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            level = match.group(1).lower()
            # Si auto-tuning está habilitado, window scaling está habilitado
            enabled = level in ["normal", "experimental", "highly restricted", "restricted"]
        else:
            # Revisar registro
            value = self._read_registry_dword(self.TCP_PARAMS, "Tcp1323Opts")
            enabled = (value & 0x1) == 0x1 if value is not None else True  # Bit 0
        
        self.detected_states["window_scaling"] = OptimizationState(
            name="TCP Window Scaling",
            enabled=enabled,
            current_value="enabled" if enabled else "disabled",
            recommended_value="enabled",
            registry_path=self.TCP_PARAMS,
            registry_key="Tcp1323Opts"
        )
    
    def _detect_timestamps(self):
        """Detectar TCP Timestamps"""
        value = self._read_registry_dword(self.TCP_PARAMS, "Tcp1323Opts")
        
        if value is not None:
            enabled = (value & 0x2) == 0x2  # Bit 1
        else:
            enabled = True  # Por defecto habilitado
        
        self.detected_states["timestamps"] = OptimizationState(
            name="TCP Timestamps",
            enabled=enabled,
            current_value=value,
            recommended_value=3,  # Ambos bits
            registry_path=self.TCP_PARAMS,
            registry_key="Tcp1323Opts"
        )
    
    def _detect_sack(self):
        """Detectar SACK (Selective Acknowledgment)"""
        value = self._read_registry_dword(self.TCP_PARAMS, "SackOpts")
        enabled = value == 1 if value is not None else True  # Habilitado por defecto
        
        self.detected_states["sack"] = OptimizationState(
            name="SACK (Selective ACK)",
            enabled=enabled,
            current_value=value,
            recommended_value=1,
            registry_path=self.TCP_PARAMS,
            registry_key="SackOpts"
        )
    
    def _detect_chimney_offload(self):
        """Detectar TCP Chimney Offload"""
        output = self._run_netsh_command("interface tcp show global")
        
        match = re.search(r"Chimney Offload State\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            state = match.group(1).lower()
            enabled = state == "enabled"
        else:
            value = self._read_registry_dword(self.TCP_PARAMS, "EnableTCPChimney")
            enabled = value == 1 if value is not None else False
        
        self.detected_states["chimney_offload"] = OptimizationState(
            name="TCP Chimney Offload",
            enabled=enabled,
            current_value="enabled" if enabled else "disabled",
            recommended_value="disabled",  # Puede causar problemas
            registry_path=self.TCP_PARAMS,
            registry_key="EnableTCPChimney"
        )
    
    def _detect_network_throttling(self):
        """Detectar Network Throttling Index"""
        value = self._read_registry_dword(
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "NetworkThrottlingIndex"
        )
        
        # 0xFFFFFFFF = deshabilitado (mejor para gaming/streaming)
        # 10 = valor por defecto
        enabled = value == 0xFFFFFFFF if value is not None else False
        
        self.detected_states["network_throttling"] = OptimizationState(
            name="Network Throttling (disabled)",
            enabled=enabled,
            current_value=value,
            recommended_value=0xFFFFFFFF,
            registry_path=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            registry_key="NetworkThrottlingIndex"
        )
    
    def _detect_task_offload(self):
        """Detectar Task Offload (TSO/GSO)"""
        output = self._run_netsh_command("interface tcp show global")
        
        match = re.search(r"Task Offload\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            state = match.group(1).lower()
            enabled = state == "enabled"
        else:
            # Asumir habilitado si no se encuentra
            enabled = True
        
        self.detected_states["task_offload"] = OptimizationState(
            name="Task Offload (TSO/GSO)",
            enabled=enabled,
            current_value="enabled" if enabled else "disabled",
            recommended_value="enabled"
        )
    
    def _detect_nagle(self):
        """Detectar Nagle's Algorithm"""
        value = self._read_registry_dword(self.TCP_PARAMS, "TcpNoDelay")
        
        # TcpNoDelay = 1 significa Nagle deshabilitado (mejor para gaming)
        nagle_disabled = value == 1 if value is not None else False
        
        self.detected_states["nagle"] = OptimizationState(
            name="Nagle Algorithm (disabled)",
            enabled=nagle_disabled,
            current_value=value,
            recommended_value=1,  # Deshabilitar para baja latencia
            registry_path=self.TCP_PARAMS,
            registry_key="TcpNoDelay"
        )
    
    def _detect_auto_tuning(self):
        """Detectar Auto-Tuning Level"""
        output = self._run_netsh_command("interface tcp show global")
        
        match = re.search(r"Receive Window Auto-Tuning Level\s*:\s*(\w+)", output, re.IGNORECASE)
        
        if match:
            level = match.group(1).lower()
            # "normal" o "experimental" son buenos
            enabled = level in ["normal", "experimental"]
            current = level
        else:
            enabled = True
            current = "normal"
        
        self.detected_states["auto_tuning"] = OptimizationState(
            name="Auto-Tuning Level",
            enabled=enabled,
            current_value=current,
            recommended_value="normal"
        )
    
    def _detect_dca(self):
        """Detectar DCA (Direct Cache Access)"""
        value = self._read_registry_dword(self.AFD_PARAMS, "EnableDynamicBacklog")
        enabled = value == 1 if value is not None else False
        
        self.detected_states["dca"] = OptimizationState(
            name="DCA (Direct Cache Access)",
            enabled=enabled,
            current_value=value,
            recommended_value=1,
            registry_path=self.AFD_PARAMS,
            registry_key="EnableDynamicBacklog"
        )
    
    def get_optimization_state(self, optimization_id: str) -> Optional[OptimizationState]:
        """Obtener estado de una optimización específica"""
        return self.detected_states.get(optimization_id)
    
    def get_enabled_optimizations(self) -> Dict[str, OptimizationState]:
        """Obtener solo optimizaciones habilitadas"""
        return {
            opt_id: state 
            for opt_id, state in self.detected_states.items() 
            if state.enabled
        }
    
    def get_disabled_optimizations(self) -> Dict[str, OptimizationState]:
        """Obtener optimizaciones deshabilitadas"""
        return {
            opt_id: state 
            for opt_id, state in self.detected_states.items() 
            if not state.enabled
        }
    
    def get_summary(self) -> Dict[str, int]:
        """Resumen de optimizaciones"""
        total = len(self.detected_states)
        enabled = len(self.get_enabled_optimizations())
        
        return {
            'total': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'percentage': int((enabled / total * 100) if total > 0 else 0)
        }


# Función auxiliar para uso rápido
def detect_optimizations() -> Dict[str, OptimizationState]:
    """
    Detectar todas las optimizaciones de red
    
    Returns:
        Dict con estado de cada optimización
    """
    detector = OptimizationDetector()
    return detector.detect_all()


if __name__ == "__main__":
    # Test
    from ..utils.logger import log_info
    
    log_info("🔍 Detectando optimizaciones de red...")
    
    detector = OptimizationDetector()
    states = detector.detect_all()
    
    log_info(f"📊 Resumen: {detector.get_summary()}")
    
    log_info("✅ Optimizaciones HABILITADAS:")
    for opt_id, state in detector.get_enabled_optimizations().items():
        log_info(f"  • {state.name}: {state.current_value}")
    
    log_info("❌ Optimizaciones DESHABILITADAS:")
    for opt_id, state in detector.get_disabled_optimizations().items():
        log_info(f"  • {state.name}: {state.current_value} (recomendado: {state.recommended_value})")
