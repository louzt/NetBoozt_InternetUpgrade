"""
NetBoozt - Interfaz Moderna con CustomTkinter
By LOUST (www.loust.pro)
"""

import customtkinter as ctk
from PIL import Image
import subprocess
import threading
import sys
from pathlib import Path
from typing import Dict, List, Callable, Optional
from datetime import datetime

# Importar módulos de NetBoozt
try:
    from ..monitoring.realtime_monitor import NetworkMonitor, NetworkSnapshot
    from ..monitoring.adapter_manager import AdapterManager, get_adapter_manager
    from ..monitoring.alert_system import get_alert_system, AlertType
    from ..optimizations.detection import OptimizationDetector
    from ..optimizations.optimizer import NetworkOptimizer, ApplyResult, OptimizationResult
    from ..storage.db_manager import NetBooztStorage
    from ..storage.backup_system import get_backup_system
    from ..utils.logger import log_info, log_warning, log_error
    from .dashboard import NetworkDashboard
    from .about_tab import AboutTab
    from .readme_tab import ReadmeTab
    from .docs_tab import DocsTab
    from .github_tab import GitHubTab
    from .theme import *
    from .theme_manager import get_theme_manager, ThemeMode
    from .advanced_graphs import AdvancedGraphsTab
except ImportError:
    # Fallback si se ejecuta directamente
    NetworkMonitor = None
    AdapterManager = None
    get_adapter_manager = None
    get_alert_system = None
    AlertType = None
    OptimizationDetector = None
    NetBooztStorage = None
    get_backup_system = None
    NetworkDashboard = None
    AboutTab = None
    ReadmeTab = None
    DocsTab = None
    GitHubTab = None
    get_theme_manager = None
    ThemeMode = None
    AdvancedGraphsTab = None


class ModernNetBoozt(ctk.CTk):
    """Interfaz moderna de NetBoozt"""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar theme manager
        self.theme_manager = get_theme_manager() if get_theme_manager else None
        if self.theme_manager:
            self.theme_manager.on_theme_change(self._on_theme_changed)
        
        # Configuración de ventana
        self.title("NetBoozt - Network Performance Optimizer")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        
        # Registrar cleanup al cerrar
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iconos y assets
        self.setup_assets()
        
        # Estado de optimizaciones
        self.optimizations_state: Dict[str, bool] = {}
        self.is_admin = self.check_admin()
        
        # Inicializar módulos
        self.storage = NetBooztStorage() if NetBooztStorage else None
        self.detector = OptimizationDetector() if OptimizationDetector else None
        self.optimizer = NetworkOptimizer() if NetworkOptimizer else None
        self.adapter_manager = get_adapter_manager() if get_adapter_manager else None
        self.network_monitor: Optional[NetworkMonitor] = None
        self.current_adapter = "Ethernet"  # Default
        
        # Auto-Failover components
        self.dns_health_checker = None
        self.auto_failover_manager = None
        
        # Alert and Backup systems
        self.alert_system = get_alert_system() if get_alert_system else None
        self.backup_system = get_backup_system() if get_backup_system else None
        
        # Registrar callback de alertas
        if self.alert_system:
            self.alert_system.on_alert(self._on_alert_triggered)
        
        # Control de loops
        self._dashboard_update_id = None
        self._dashboard_active = False
        
        # Crear interfaz
        self.setup_ui()
        
        # Detectar estado actual de optimizaciones
        self.detect_current_state()
        
        # Iniciar monitor de red
        self.start_network_monitoring()
    
    def start_network_monitoring(self):
        """Iniciar monitoreo de red en tiempo real"""
        if NetworkMonitor:
            self.network_monitor = NetworkMonitor(self.current_adapter, interval=1.0)
            self.network_monitor.register_callback(self.on_network_update)
            self.network_monitor.start()
            
            # Marcar dashboard como activo
            self._dashboard_active = True
            # Iniciar loop de actualización
            self.update_dashboard_loop()
    
    def on_network_update(self, snapshot: 'NetworkSnapshot'):
        """Callback cuando hay nueva data de red"""
        if self.storage:
            # Guardar métrica en DB
            metric_data = {
                'adapter': snapshot.adapter,
                'bytes_sent': snapshot.bytes_sent,
                'bytes_recv': snapshot.bytes_recv,
                'packets_sent': snapshot.packets_sent,
                'packets_recv': snapshot.packets_recv,
                'errors_in': snapshot.errors_in,
                'errors_out': snapshot.errors_out,
                'drops_in': snapshot.drops_in,
                'drops_out': snapshot.drops_out
            }
            self.storage.save_metric(metric_data)
    
    def update_dashboard_loop(self):
        """Loop de actualización del dashboard"""
        # Cancelar loop anterior si existe
        if self._dashboard_update_id:
            self.after_cancel(self._dashboard_update_id)
            self._dashboard_update_id = None
        
        # Solo actualizar si dashboard está activo
        if not self._dashboard_active:
            return
        
        if hasattr(self, 'dashboard_tab') and self.network_monitor:
            snapshot = self.network_monitor.get_current_snapshot()
            
            if snapshot:
                # Actualizar gráficas del dashboard
                self.dashboard_tab.update_graphs(
                    snapshot.timestamp,
                    {
                        'download_mbps': snapshot.download_rate_mbps,
                        'upload_mbps': snapshot.upload_rate_mbps,
                        'latency_ms': self.network_monitor.get_current_latency(),
                        'packets_sent_per_sec': snapshot.packets_sent_per_sec,
                        'packets_recv_per_sec': snapshot.packets_recv_per_sec,
                        'errors_per_sec': snapshot.errors_per_sec,
                        'drops_per_sec': snapshot.drops_per_sec
                    }
                )
                
                # Actualizar gráficas avanzadas si existen
                if hasattr(self, 'graphs_tab'):
                    from datetime import datetime
                    self.graphs_tab.update_graphs(
                        datetime.now(),
                        {
                            'download_mbps': snapshot.download_rate_mbps,
                            'upload_mbps': snapshot.upload_rate_mbps,
                            'latency_ms': self.network_monitor.get_current_latency(),
                            'packet_loss': 0  # TODO: calcular packet loss real
                        }
                    )
                
                # Verificar alertas
                if self.alert_system and AlertType:
                    latency = self.network_monitor.get_current_latency()
                    if latency > 0:
                        self.alert_system.check_metric(AlertType.LATENCY_HIGH, latency)
                    
                    # Verificar velocidad
                    if snapshot.download_rate_mbps < 10:
                        self.alert_system.check_metric(AlertType.SPEED_LOW, snapshot.download_rate_mbps)
                
                # Actualizar estadísticas
                avg_rates = self.network_monitor.get_average_rates(10)
                peak_rates = self.network_monitor.get_peak_rates(60)
                
                self.dashboard_tab.update_stats({
                    'avg_download_mbps': avg_rates['download_mbps'],
                    'avg_upload_mbps': avg_rates['upload_mbps'],
                    'peak_download_mbps': peak_rates['peak_download_mbps'],
                    'peak_upload_mbps': peak_rates['peak_upload_mbps'],
                    'avg_latency_ms': self.network_monitor.get_average_latency(10),
                    'packet_loss_percent': 0,
                    'total_errors': snapshot.errors_in + snapshot.errors_out
                })
        
        # Programar siguiente actualización solo si dashboard está activo
        if self._dashboard_active:
            self._dashboard_update_id = self.after(1000, self.update_dashboard_loop)
    
    def setup_assets(self):
        """Configurar assets (logo, iconos)"""
        import sys
        
        # Detectar si estamos en .exe frozen
        if getattr(sys, 'frozen', False):
            # Modo frozen: assets están junto al .exe
            base_dir = Path(sys.executable).parent
            assets_dir = base_dir / "assets"
        else:
            # Modo desarrollo
            assets_dir = Path(__file__).parent.parent.parent / "assets"
        
        # Logo LOUST
        self.logo_path = assets_dir / "loust_logo.png"
        
        # Si existe el logo, cargarlo
        if self.logo_path.exists():
            try:
                self.logo_image = ctk.CTkImage(
                    light_image=Image.open(self.logo_path),
                    dark_image=Image.open(self.logo_path),
                    size=(60, 60)
                )
            except Exception as e:
                # Si falla, log y usar None
                try:
                    from utils.logger import log_warning
                    log_warning(f"Failed to load logo from {self.logo_path}: {e}")
                except Exception:
                    # Logger import puede fallar en modo frozen
                    pass
                self.logo_image = None
        else:
            self.logo_image = None
    
    def check_admin(self) -> bool:
        """Verificar si tiene permisos de administrador"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            # Platform not supported or ctypes error
            return False
    
    def setup_ui(self):
        """Crear interfaz de usuario"""
        
        # Grid layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar (menú lateral)
        self.create_sidebar()
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_MAIN)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Permitir que tabs_container use toda la altura
        
        # Header
        self.create_header()
        
        # Tabs para diferentes secciones
        self.create_tabs()
    
    def create_sidebar(self):
        """Crear sidebar con navegación"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        # Logo
        if self.logo_image:
            logo_label = ctk.CTkLabel(
                self.sidebar,
                image=self.logo_image,
                text=""
            )
            logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Título
        title = ctk.CTkLabel(
            self.sidebar,
            text="NetBoozt",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=1, column=0, padx=20, pady=(0, 5))
        
        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Network Optimizer",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        # Botones de navegación
        self.nav_buttons = {}
        
        nav_items = [
            ("📊 Dashboard", "dashboard"),
            ("🚀 Optimizaciones", "optimizations"),
            ("📈 Estado de Red", "status"),
            ("🔄 Failover DNS", "failover"),
            ("📊 Gráficas", "graphs"),
            ("🔔 Alertas", "alerts"),
            ("💾 Backups", "backups"),
            ("⚙️ Configuración", "settings"),
            ("ℹ️ About", "about"),
            ("📄 README", "readme"),
            ("📖 Documentación", "docs"),
            ("🔗 GitHub", "github"),
        ]
        
        for idx, (text, key) in enumerate(nav_items, start=3):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
                fg_color="transparent",
                hover_color=BG_HOVER,
                text_color=TEXT_SECONDARY,
                anchor="w",
                command=lambda k=key: self.switch_tab(k)
            )
            btn.grid(row=idx, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[key] = btn
        
        # Estado admin
        admin_status = "✅ Administrador" if self.is_admin else "⚠️ Requiere Admin"
        admin_color = "green" if self.is_admin else "orange"
        
        admin_label = ctk.CTkLabel(
            self.sidebar,
            text=admin_status,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=admin_color
        )
        admin_label.grid(row=10, column=0, padx=20, pady=(10, 5))
        
        # Footer
        footer = ctk.CTkLabel(
            self.sidebar,
            text="by LOUST\nwww.loust.pro",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        footer.grid(row=11, column=0, padx=20, pady=(5, 20))
    
    def create_header(self):
        """Crear header con título y acciones"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Título de sección
        self.section_title = ctk.CTkLabel(
            header_frame,
            text="Optimizaciones TCP/IP",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.section_title.grid(row=0, column=0, sticky="w")
        
        # Botón de aplicar todo
        self.apply_all_btn = ctk.CTkButton(
            header_frame,
            text="⚡ Aplicar Todo",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self.apply_all_optimizations
        )
        self.apply_all_btn.grid(row=0, column=1, padx=10)
    
    def create_tabs(self):
        """Crear tabs con contenido"""
        # Frame contenedor para tabs
        self.tabs_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tabs_container.grid(row=1, column=0, sticky="nsew")
        self.tabs_container.grid_columnconfigure(0, weight=1)
        self.tabs_container.grid_rowconfigure(0, weight=1)
        
        # Crear contenido de cada tab
        self.tab_frames = {}
        
        # Tab Dashboard (NUEVO)
        if NetworkDashboard:
            self.dashboard_tab = NetworkDashboard(self.tabs_container)
            self.tab_frames["dashboard"] = self.dashboard_tab
        
        # Tab Optimizaciones
        self.tab_frames["optimizations"] = self.create_optimizations_tab()
        
        # Tab Estado
        self.tab_frames["status"] = self.create_status_tab()
        
        # Tab Failover
        self.tab_frames["failover"] = self.create_failover_tab()
        
        # Tab Gráficas Avanzadas (NUEVO)
        if AdvancedGraphsTab:
            self.graphs_tab = AdvancedGraphsTab(self.tabs_container)
            self.tab_frames["graphs"] = self.graphs_tab
        
        # Tab Alertas (NUEVO)
        self.tab_frames["alerts"] = self.create_alerts_tab()
        
        # Tab Backups (NUEVO)
        self.tab_frames["backups"] = self.create_backups_tab()
        
        # Tab Settings
        self.tab_frames["settings"] = self.create_settings_tab()
        
        # Tab About
        if AboutTab:
            self.tab_frames["about"] = AboutTab(self.tabs_container)
        
        # Tab README
        if ReadmeTab:
            self.tab_frames["readme"] = ReadmeTab(self.tabs_container)
        
        # Tab Documentation
        if DocsTab:
            self.tab_frames["docs"] = DocsTab(self.tabs_container)
        
        # Tab GitHub
        if GitHubTab:
            self.tab_frames["github"] = GitHubTab(self.tabs_container)
        
        # Mostrar tab inicial (Dashboard)
        self.switch_tab("dashboard")
    
    def create_optimizations_tab(self) -> ctk.CTkScrollableFrame:
        """Crear tab de optimizaciones"""
        frame = ctk.CTkScrollableFrame(
            self.tabs_container,
            fg_color="transparent"
        )
        
        # Diccionario para guardar referencias a los switches
        self.optimization_switches: Dict[str, ctk.CTkSwitch] = {}
        
        # Categorías de optimizaciones
        categories = {
            "🚀 TCP Congestion Control": [
                ("HyStart++", "Arranque rápido similar a BBR de Linux", "hystart"),
                ("PRR (Proportional Rate Reduction)", "Recuperación suave de pérdidas", "prr"),
                ("TCP Pacing", "Anti-bufferbloat, espaciado de paquetes", "pacing"),
            ],
            "📡 Receive Side Scaling (RSS)": [
                ("RSS Habilitado", "Distribuir carga entre CPUs", "rss_enabled"),
                ("RSS Queue Count", "Optimizar número de colas", "rss_queues"),
            ],
            "🌐 Network Stack": [
                ("ECN (Explicit Congestion Notification)", "Señales de congestión sin pérdida", "ecn"),
                ("TCP Fast Open", "Conexiones más rápidas", "tfo"),
                ("TCP Window Scaling", "Ventanas grandes para alta latencia", "window_scaling"),
            ],
            "⚡ Performance Tweaks": [
                ("Optimized RTO", "Timeouts más rápidos", "rto"),
                ("TSO/GSO Offload", "Offload de segmentación a NIC", "tso"),
                ("Chimney Offload", "Offload TCP a NIC (experimental)", "chimney"),
            ]
        }
        
        row = 0
        for category, opts in categories.items():
            # Header de categoría
            cat_label = ctk.CTkLabel(
                frame,
                text=category,
                font=ctk.CTkFont(size=18, weight="bold"),
                anchor="w"
            )
            cat_label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(20, 10))
            row += 1
            
            # Optimizaciones
            for name, desc, key in opts:
                # Obtener estado detectado (ya viene de detect_current_state)
                current_state = self.optimizations_state.get(key, False)
                
                # Checkbox/Switch PRE-SELECCIONADO según estado actual
                var = ctk.BooleanVar(value=current_state)
                switch = ctk.CTkSwitch(
                    frame,
                    text="",
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    command=lambda k=key, v=var: self.toggle_optimization(k, v.get())
                )
                switch.grid(row=row, column=0, padx=(0, 10), sticky="w")
                
                # Guardar referencia al switch
                self.optimization_switches[key] = switch
                
                # Nombre
                name_label = ctk.CTkLabel(
                    frame,
                    text=name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                name_label.grid(row=row, column=1, sticky="w", padx=10)
                
                # Descripción
                desc_label = ctk.CTkLabel(
                    frame,
                    text=desc,
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                    anchor="w"
                )
                desc_label.grid(row=row, column=2, sticky="w", padx=10)
                
                row += 1
        
        # ========== BOTONES DE ACCIÓN ==========
        actions_frame = ctk.CTkFrame(frame, fg_color="transparent")
        actions_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=30)
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Botón Refresh (forzar re-detección)
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh Estado",
            font=ctk.CTkFont(size=14),
            height=45,
            fg_color="#404040",
            hover_color="#505050",
            command=self.force_refresh_optimizations
        )
        refresh_btn.grid(row=0, column=0, padx=10, sticky="ew")
        
        # Botón Aplicar Selección
        apply_btn = ctk.CTkButton(
            actions_frame,
            text="✅ Aplicar Optimizaciones",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color=PRIMARY,
            hover_color="#00b894",
            command=self.apply_selected_optimizations
        )
        apply_btn.grid(row=0, column=1, padx=10, sticky="ew")
        
        # Botón Revertir Todo
        revert_btn = ctk.CTkButton(
            actions_frame,
            text="↩️ Revertir Todo",
            font=ctk.CTkFont(size=14),
            height=45,
            fg_color="#d63031",
            hover_color="#e74c3c",
            command=self.revert_all_optimizations
        )
        revert_btn.grid(row=0, column=2, padx=10, sticky="ew")
        
        # Info sobre reinicio
        if not self.is_admin:
            admin_warning = ctk.CTkLabel(
                frame,
                text="⚠️ Algunas optimizaciones requieren permisos de Administrador",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_WARNING
            )
            admin_warning.grid(row=row+1, column=0, columnspan=3, pady=10)
        
        return frame
    
    def create_status_tab(self) -> ctk.CTkScrollableFrame:
        """Crear tab de estado de red con detección de prioridades"""
        frame = ctk.CTkScrollableFrame(self.tabs_container, fg_color="transparent")
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="📡 Estado de Adaptadores de Red",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 5), anchor="w")
        
        subtitle = ctk.CTkLabel(
            frame,
            text="Prioridades automáticas y métricas de interfaz",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle.pack(pady=(0, 20), anchor="w")
        
        # Contenedor de adaptadores
        self.adapters_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.adapters_container.pack(fill="both", expand=True, pady=10)
        
        # Botón de actualizar
        refresh_frame = ctk.CTkFrame(frame, fg_color="transparent")
        refresh_frame.pack(fill="x", pady=20)
        
        refresh_btn = ctk.CTkButton(
            refresh_frame,
            text="🔄 Actualizar Estado",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.refresh_adapters_display
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Info de prioridad
        info_label = ctk.CTkLabel(
            refresh_frame,
            text="💡 Métrica más baja = mayor prioridad. Windows usa el adaptador con menor métrica.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(side="left", padx=20)
        
        # Cargar adaptadores inicialmente
        self.refresh_adapters_display()
        
        return frame
    
    def refresh_adapters_display(self):
        """Actualizar display de adaptadores"""
        if not self.adapter_manager:
            return
        
        # Limpiar container
        for widget in self.adapters_container.winfo_children():
            widget.destroy()
        
        # Redetectar adaptadores
        self.adapter_manager._detect_adapters()
        adapters = self.adapter_manager.get_adapters_sorted_by_priority()
        
        if not adapters:
            no_adapters = ctk.CTkLabel(
                self.adapters_container,
                text="⚠️ No se encontraron adaptadores",
                font=ctk.CTkFont(size=14),
                text_color="orange"
            )
            no_adapters.pack(pady=20)
            return
        
        # Crear card para cada adaptador
        for idx, adapter in enumerate(adapters, 1):
            self._create_adapter_card(self.adapters_container, adapter, idx)
    
    def _create_adapter_card(self, parent, adapter, rank: int):
        """Crear card de adaptador"""
        # Frame principal con borde según estado
        border_color = PRIMARY if adapter.is_active else BORDER_DEFAULT
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, border_color=border_color, border_width=2, corner_radius=RADIUS_LARGE)
        card.pack(fill="x", padx=10, pady=8)
        
        # Header con nombre y badge de prioridad
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Badge de ranking
        rank_badge = ctk.CTkLabel(
            header,
            text=f"#{rank}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY if rank == 1 else TEXT_DISABLED,
            fg_color=PRIMARY if rank == 1 else BG_HOVER,
            corner_radius=6,
            width=40,
            height=30
        )
        rank_badge.pack(side="left", padx=(0, 10))
        
        # Nombre del adaptador
        name_label = ctk.CTkLabel(
            header,
            text=adapter.name,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", padx=5)
        
        # Status badge
        status_emoji = "✅" if adapter.is_active else "❌"
        status_text = adapter.status.value
        status_label = ctk.CTkLabel(
            header,
            text=f"{status_emoji} {status_text}",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SUCCESS if adapter.is_active else TEXT_ERROR
        )
        status_label.pack(side="right", padx=10)
        
        # Grid de información
        info_grid = ctk.CTkFrame(card, fg_color="transparent")
        info_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        info_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Row 1: Métrica, Velocidad, MAC
        self._add_info_row(info_grid, 0, [
            ("📊 Métrica (Prioridad)", str(adapter.metric), TEXT_WARNING if rank == 1 else TEXT_SECONDARY),
            ("⚡ Velocidad", f"{adapter.speed_mbps} Mbps", PRIMARY),
            ("🔑 MAC", adapter.mac_address, TEXT_DISABLED)
        ])
        
        # Row 2: IP, Gateway, MTU
        self._add_info_row(info_grid, 1, [
            ("🌐 IPv4", adapter.ipv4_address or "N/A", PRIMARY),
            ("🚪 Gateway", adapter.default_gateway or "N/A", TEXT_WARNING),
            ("📦 MTU", str(adapter.mtu), TEXT_DISABLED)
        ])
        
        # Row 3: DNS Provider y servidores
        dns_display = ", ".join(adapter.dns_servers[:2]) if adapter.dns_servers else "DHCP"
        self._add_info_row(info_grid, 2, [
            ("🎯 DNS Provider", adapter.dns_provider, TEXT_WARNING),
            ("📡 Servidores DNS", dns_display, TEXT_DISABLED),
            ("🔧 DHCP", "Sí" if adapter.dhcp_enabled else "No", TEXT_DISABLED)
        ])
    
    def _add_info_row(self, parent, row: int, items: list):
        """Agregar fila de información"""
        for col, (label, value, color) in enumerate(items):
            item_frame = ctk.CTkFrame(parent, fg_color=BG_HOVER, corner_radius=RADIUS_SMALL)
            item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            label_widget = ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(size=10),
                text_color=TEXT_DISABLED
            )
            label_widget.pack(pady=(8, 2))
            
            value_widget = ctk.CTkLabel(
                item_frame,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color
            )
            value_widget.pack(pady=(0, 8))
    
    def create_failover_tab(self) -> ctk.CTkScrollableFrame:
        """Crear tab de DNS Failover con detección del tier activo"""
        frame = ctk.CTkScrollableFrame(self.tabs_container, fg_color="transparent")
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="🔄 DNS Failover de 7 Niveles",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 5), anchor="w")
        
        # Descripción
        desc = ctk.CTkLabel(
            frame,
            text="Configuración automática de DNS con 7 niveles de fallback para máxima disponibilidad",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=800,
            justify="left"
        )
        desc.pack(pady=(0, 20), anchor="w")
        
        # NUEVO: Auto-Failover Control
        autofailover_frame = ctk.CTkFrame(frame, fg_color=BG_CARD)
        autofailover_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        autofailover_header = ctk.CTkLabel(
            autofailover_frame,
            text="⚡ Auto-Failover Automático",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        autofailover_header.pack(pady=(15, 5), padx=20, anchor="w")
        
        autofailover_desc = ctk.CTkLabel(
            autofailover_frame,
            text="Detecta automáticamente fallos de DNS y cambia al siguiente tier funcional",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        autofailover_desc.pack(pady=(0, 10), padx=20, anchor="w")
        
        # Switch de auto-failover
        self.autofailover_switch = ctk.CTkSwitch(
            autofailover_frame,
            text="Habilitar Auto-Failover",
            font=ctk.CTkFont(size=14),
            command=self.toggle_autofailover
        )
        self.autofailover_switch.pack(pady=(5, 15), padx=20, anchor="w")
        
        # Estado de health checking
        self.health_status_label = ctk.CTkLabel(
            autofailover_frame,
            text="Estado: Deshabilitado",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DISABLED
        )
        self.health_status_label.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Contenedor de DNS tiers
        self.dns_tiers_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.dns_tiers_container.pack(fill="both", expand=True, pady=10)
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=20)
        
        refresh_dns_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar Estado DNS",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.refresh_dns_display
        )
        refresh_dns_btn.pack(side="left", padx=10)
        
        info_label = ctk.CTkLabel(
            actions_frame,
            text="💡 El tier resaltado en verde es el que está actualmente configurado en tu adaptador prioritario",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(side="left", padx=20)
        
        # Cargar DNS tiers inicialmente
        self.refresh_dns_display()
        
        return frame
    
    def refresh_dns_display(self):
        """Actualizar display de DNS tiers"""
        if not self.adapter_manager:
            return
        
        # Limpiar container
        for widget in self.dns_tiers_container.winfo_children():
            widget.destroy()
        
        # Obtener tiers con detección del activo
        tiers = self.adapter_manager.get_dns_fallback_status()
        
        # Crear card para cada tier
        for tier in tiers:
            self._create_dns_tier_card(self.dns_tiers_container, tier)
    
    def _create_dns_tier_card(self, parent, tier):
        """Crear card de DNS tier"""
        # Border color según si está activo
        border_color = TEXT_SUCCESS if tier.active else BORDER_DEFAULT
        border_width = 3 if tier.active else 1
        
        card = ctk.CTkFrame(
            parent, 
            fg_color=BG_CARD if not tier.active else "#0a1a0a",
            border_color=border_color,
            border_width=border_width
        )
        card.pack(fill="x", padx=10, pady=6)
        
        # Container principal horizontal
        main_container = ctk.CTkFrame(card, fg_color="transparent")
        main_container.pack(fill="x", padx=15, pady=12)
        
        # Tier badge
        tier_badge = ctk.CTkLabel(
            main_container,
            text=f"Tier {tier.tier}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
            fg_color=PRIMARY if tier.tier <= 3 else TEXT_DISABLED,
            corner_radius=6,
            width=70,
            height=35
        )
        tier_badge.pack(side="left", padx=(0, 15))
        
        # Info container
        info_container = ctk.CTkFrame(main_container, fg_color="transparent")
        info_container.pack(side="left", fill="x", expand=True)
        
        # Provider name con badge de ACTIVO
        name_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        name_frame.pack(fill="x", pady=(0, 5))
        
        provider_label = ctk.CTkLabel(
            name_frame,
            text=tier.provider,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        provider_label.pack(side="left")
        
        if tier.active:
            active_badge = ctk.CTkLabel(
                name_frame,
                text="✓ ACTIVO",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=TEXT_SUCCESS,
                fg_color=SUCCESS_BG,
                corner_radius=4,
                padx=10,
                pady=4
            )
            active_badge.pack(side="left", padx=10)
        
        # DNS servers
        if tier.tier < 7:  # No mostrar para DHCP
            dns_text = f"Primary: {tier.primary}  •  Secondary: {tier.secondary}"
            dns_label = ctk.CTkLabel(
                info_container,
                text=dns_text,
                font=ctk.CTkFont(size=12, family="Consolas"),
                text_color=TEXT_DISABLED,
                anchor="w"
            )
            dns_label.pack(fill="x")
        else:
            dns_label = ctk.CTkLabel(
                info_container,
                text="DNS automático del router (DHCP)",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_DISABLED,
                anchor="w"
            )
            dns_label.pack(fill="x")
        
        # Botón de aplicar (solo si no está activo)
        if not tier.active:
            apply_btn = ctk.CTkButton(
                main_container,
                text="Aplicar",
                font=ctk.CTkFont(size=12),
                width=80,
                height=35,
                command=lambda t=tier.tier: self.apply_dns_tier(t)
            )
            apply_btn.pack(side="right", padx=(10, 0))
    
    def apply_dns_tier(self, tier_number: int):
        """Aplicar un tier de DNS"""
        if not self.adapter_manager:
            return
        
        success = self.adapter_manager.apply_dns_tier(tier_number)
        
        if success:
            log_info(f"DNS Tier {tier_number} aplicado correctamente")
            # Actualizar display
            self.after(1000, self.refresh_dns_display)
        else:
            log_error(f"Error aplicando DNS Tier {tier_number}")
        apply_btn = ctk.CTkButton(
            frame,
            text="✅ Aplicar Configuración DNS",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            command=self.apply_dns_failover
        )
        apply_btn.grid(row=10, column=0, pady=30)
        
        return frame
    
    def create_alerts_tab(self) -> ctk.CTkScrollableFrame:
        """Crear tab de alertas"""
        frame = ctk.CTkScrollableFrame(self.tabs_container, fg_color="transparent")
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="🔔 Sistema de Alertas",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 5), anchor="w")
        
        desc = ctk.CTkLabel(
            frame,
            text="Configurar thresholds y ver historial de alertas",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc.pack(pady=(0, 20), anchor="w")
        
        # Alertas activas
        active_frame = ctk.CTkFrame(frame, fg_color=BG_CARD)
        active_frame.pack(fill="x", pady=10, padx=10)
        
        active_header = ctk.CTkLabel(
            active_frame,
            text="⚠️ Alertas Activas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        active_header.pack(pady=15, padx=20, anchor="w")
        
        # Container de alertas activas (dinámico)
        self.active_alerts_container = ctk.CTkFrame(active_frame, fg_color="transparent")
        self.active_alerts_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        # Configuración de thresholds
        config_frame = ctk.CTkFrame(frame, fg_color=BG_CARD)
        config_frame.pack(fill="x", pady=10, padx=10)
        
        config_header = ctk.CTkLabel(
            config_frame,
            text="⚙️ Configuración de Thresholds",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        config_header.pack(pady=15, padx=20, anchor="w")
        
        # Thresholds configurables
        thresholds = [
            ("Latencia Alta", "ms", "latency_high", 100.0),
            ("Pérdida de Paquetes", "%", "packet_loss_high", 2.0),
            ("Velocidad Baja", "Mbps", "speed_low", 10.0),
        ]
        
        for label, unit, key, default in thresholds:
            row = ctk.CTkFrame(config_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(
                row,
                text=f"{label}:",
                font=ctk.CTkFont(size=14),
                width=200
            ).pack(side="left")
            
            entry = ctk.CTkEntry(
                row,
                width=100,
                placeholder_text=str(default)
            )
            entry.pack(side="left", padx=10)
            entry.insert(0, str(default))
            
            ctk.CTkLabel(
                row,
                text=unit,
                font=ctk.CTkFont(size=12),
                text_color="gray"
            ).pack(side="left")
        
        # Botón aplicar
        apply_btn = ctk.CTkButton(
            config_frame,
            text="💾 Guardar Configuración",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.apply_alert_thresholds
        )
        apply_btn.pack(pady=20)
        
        # Actualizar alertas activas
        self.refresh_active_alerts()
        
        return frame
    
    def create_backups_tab(self) -> ctk.CTkScrollableFrame:
        """Crear tab de backups"""
        frame = ctk.CTkScrollableFrame(self.tabs_container, fg_color="transparent")
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text="💾 Backups de Configuración",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 5), anchor="w")
        
        desc = ctk.CTkLabel(
            frame,
            text="Crear snapshots y restaurar configuración de red",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc.pack(pady=(0, 20), anchor="w")
        
        # Botones de acción
        actions_frame = ctk.CTkFrame(frame, fg_color="transparent")
        actions_frame.pack(fill="x", pady=10)
        
        create_backup_btn = ctk.CTkButton(
            actions_frame,
            text="📸 Crear Backup Ahora",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.create_backup_now
        )
        create_backup_btn.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Actualizar Lista",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.refresh_backups_list
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Container de backups (dinámico)
        self.backups_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.backups_container.pack(fill="both", expand=True, pady=10)
        
        # Cargar lista inicial
        self.refresh_backups_list()
        
        return frame
    
    def create_settings_tab(self) -> ctk.CTkFrame:
        """Crear tab de configuración"""
        frame = ctk.CTkFrame(self.tabs_container, fg_color="transparent")
        
        title = ctk.CTkLabel(
            frame,
            text="Configuración",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=20, anchor="w")
        
        # Opciones
        settings_frame = ctk.CTkFrame(frame)
        settings_frame.pack(fill="both", expand=True, pady=10)
        
        # NUEVO: Theme Toggle
        theme_frame = ctk.CTkFrame(settings_frame)
        theme_frame.pack(fill="x", pady=15, padx=20)
        
        theme_label = ctk.CTkLabel(
            theme_frame,
            text="🎨 Tema de Interfaz",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        theme_label.pack(side="left", padx=10)
        
        theme_btn = ctk.CTkButton(
            theme_frame,
            text="🌙 Modo Oscuro" if self.theme_manager and self.theme_manager.is_dark() else "☀️ Modo Claro",
            command=self.toggle_theme,
            font=ctk.CTkFont(size=14),
            width=150
        )
        theme_btn.pack(side="right", padx=10)
        self.theme_toggle_btn = theme_btn  # Guardar referencia para actualizar texto
        
        # Inicio automático
        auto_start_switch = ctk.CTkSwitch(
            settings_frame,
            text="Ejecutar al iniciar Windows",
            font=ctk.CTkFont(size=14)
        )
        auto_start_switch.pack(pady=15, padx=20, anchor="w")
        
        # Notificaciones
        notif_switch = ctk.CTkSwitch(
            settings_frame,
            text="Mostrar notificaciones",
            font=ctk.CTkFont(size=14)
        )
        notif_switch.pack(pady=15, padx=20, anchor="w")
        
        # Modo
        mode_label = ctk.CTkLabel(
            settings_frame,
            text="Nivel de Optimización:",
            font=ctk.CTkFont(size=14)
        )
        mode_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        mode_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["Conservative", "Balanced", "Aggressive"],
            font=ctk.CTkFont(size=13)
        )
        mode_menu.pack(pady=5, padx=20, anchor="w")
        mode_menu.set("Balanced")
        
        return frame
    
    def switch_tab(self, tab_key: str):
        """Cambiar de tab"""
        # Ocultar todos
        for key, frame in self.tab_frames.items():
            frame.grid_forget()
        
        # Control de dashboard loop
        if tab_key == "dashboard":
            self._dashboard_active = True
            self.update_dashboard_loop()  # Reiniciar loop
        else:
            self._dashboard_active = False
            if self._dashboard_update_id:
                self.after_cancel(self._dashboard_update_id)
                self._dashboard_update_id = None
        
        # Mostrar seleccionado
        if tab_key in self.tab_frames:
            self.tab_frames[tab_key].grid(row=0, column=0, sticky="nsew")
        
        # Actualizar botones
        for key, btn in self.nav_buttons.items():
            if key == tab_key:
                btn.configure(fg_color=BG_HOVER, text_color=TEXT_PRIMARY)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
        
        # Actualizar título
        titles = {
            "dashboard": "Dashboard en Tiempo Real",
            "optimizations": "Optimizaciones TCP/IP",
            "status": "Estado de Adaptadores",
            "failover": "DNS Failover",
            "settings": "Configuración",
            "about": "Acerca de NetBoozt",
            "readme": "README - Guía Rápida",
            "docs": "Documentación Completa",
            "github": "GitHub & Colaboración"
        }
        self.section_title.configure(text=titles.get(tab_key, "NetBoozt"))
    
    def detect_current_state(self):
        """Detectar estado actual de optimizaciones del sistema"""
        if not self.detector:
            # Fallback: estado simulado
            self.optimizations_state = {
                "hystart": True,
                "prr": False,
                "pacing": True,
                "rss_enabled": True,
                "ecn": False,
            }
            return
        
        # PRIMERO: Intentar cargar desde cache (evita ejecutar PowerShell cada vez)
        if self.storage:
            try:
                cached_state = self.storage.load_optimization_state()
                if cached_state:
                    log_info(f"Usando cache de optimizaciones ({len(cached_state)} items)")
                    self.optimizations_state = cached_state
                    
                    # Actualizar switches si existen
                    if hasattr(self, 'optimization_switches'):
                        for key, switch in self.optimization_switches.items():
                            if key in self.optimizations_state:
                                switch.select() if self.optimizations_state[key] else switch.deselect()
                    return  # Usar cache y salir
            except Exception as e:
                log_warning(f"Error cargando cache: {e}")
        
        # SI NO HAY CACHE: Detectar optimizaciones reales (PowerShell)
        try:
            log_info("Detectando estado real de optimizaciones (PowerShell)...")
            detected = self.detector.detect_all()
            
            # Mapear estados detectados a switches de la GUI
            mapping = {
                'tcp_congestion': 'hystart',
                'rss': 'rss_enabled',
                'ecn': 'ecn',
                'tcp_fast_open': 'tfo',
                'window_scaling': 'window_scaling',
                'timestamps': 'timestamps',
                'sack': 'sack',
                'chimney_offload': 'chimney',
                'network_throttling': 'throttling_disabled',
                'task_offload': 'task_offload',
                'nagle': 'nagle_disabled',
                'auto_tuning': 'auto_tuning',
                'dca': 'dca'
            }
            
            # Actualizar estado
            for detect_key, gui_key in mapping.items():
                if detect_key in detected:
                    self.optimizations_state[gui_key] = detected[detect_key].enabled
            
            # Actualizar switches en la GUI si ya existen
            if hasattr(self, 'optimization_switches'):
                for key, switch in self.optimization_switches.items():
                    if key in self.optimizations_state:
                        switch.select() if self.optimizations_state[key] else switch.deselect()
            
            # Guardar estado detectado en DB local (cache por 1 hora)
            if self.storage:
                try:
                    self.storage.save_optimization_state(self.optimizations_state)
                    log_info("Estado de optimizaciones guardado en cache local (válido 1 hora)")
                except Exception as e:
                    log_warning(f"No se pudo guardar cache de optimizaciones: {e}")
            
            # Mostrar resumen en consola
            summary = self.detector.get_summary()
            log_info(f"{summary['enabled']}/{summary['total']} optimizaciones activas ({summary['percentage']}%)")
            
        except Exception as e:
            log_error(f"Error detectando optimizaciones: {e}")
            self.optimizations_state = {}
    
    def toggle_optimization(self, key: str, enabled: bool):
        """Toggle individual de optimización"""
        self.optimizations_state[key] = enabled
        log_info(f"Optimización {key}: {'Activada' if enabled else 'Desactivada'}")
    
    def force_refresh_optimizations(self):
        """Forzar re-detección (ignorar cache)"""
        if not self.detector:
            return
        
        log_info("Forzando re-detección de optimizaciones...")
        
        # Invalidar cache
        if self.storage:
            try:
                self.storage.save_setting('optimization_state_cache', None)
                log_info("Cache invalidado")
            except Exception as e:
                log_warning(f"Error invalidando cache: {e}")
        
        # Re-detectar
        self.detect_current_state()
        
        # Mostrar toast
        self.show_toast("✅ Estado actualizado", "Optimizaciones re-detectadas desde el sistema")
    
    def apply_selected_optimizations(self):
        """Aplicar las optimizaciones seleccionadas"""
        if not self.optimizer:
            self.show_toast("❌ Error", "Optimizer no disponible")
            return
        
        if not self.is_admin:
            self.show_admin_required_dialog()
            return
        
        # Obtener cambios a aplicar
        changes_to_apply = {}
        for key, enabled in self.optimizations_state.items():
            changes_to_apply[key] = enabled
        
        if not changes_to_apply:
            self.show_toast("ℹ️ Sin cambios", "No hay optimizaciones seleccionadas")
            return
        
        log_info(f"Aplicando {len(changes_to_apply)} optimizaciones...")
        
        # Aplicar en thread separado
        import threading
        threading.Thread(
            target=self._apply_optimizations_thread,
            args=(changes_to_apply,),
            daemon=True
        ).start()
        
        self.show_toast("⏳ Aplicando...", f"Procesando {len(changes_to_apply)} optimizaciones")
    
    def _apply_optimizations_thread(self, changes: Dict[str, bool]):
        """Thread para aplicar optimizaciones"""
        try:
            results = self.optimizer.apply_batch(changes)
            summary = self.optimizer.get_summary()
            
            success = summary['success']
            failed = summary['failed']
            reboot = summary['reboot_required']
            
            # Invalidar cache para forzar re-detección
            if self.storage:
                try:
                    self.storage.save_setting('optimization_state_cache', None)
                except Exception:
                    pass
            
            # Actualizar UI en main thread
            self.after(100, lambda: self._show_apply_results(success, failed, reboot))
            
            # Re-detectar estado
            self.after(500, self.force_refresh_optimizations)
            
        except Exception as e:
            log_error(f"Error aplicando optimizaciones: {e}")
            self.after(100, lambda: self.show_toast("❌ Error", str(e)))
    
    def _show_apply_results(self, success: int, failed: int, reboot: bool):
        """Mostrar resultados de aplicación"""
        if failed == 0:
            title = "✅ Éxito"
            msg = f"{success} optimizaciones aplicadas correctamente"
        else:
            title = "⚠️ Parcial"
            msg = f"{success} exitosas, {failed} fallidas"
        
        if reboot:
            msg += "\n\n🔄 Reinicio requerido para algunos cambios"
        
        self.show_toast(title, msg)
    
    def revert_all_optimizations(self):
        """Revertir todas las optimizaciones (restaurar defaults)"""
        if not self.is_admin:
            self.show_admin_required_dialog()
            return
        
        # Confirmar
        # TODO: Añadir diálogo de confirmación
        log_warning("Revirtiendo todas las optimizaciones...")
        
        # Desactivar todo
        reverted = {}
        for key in self.optimizations_state.keys():
            reverted[key] = False  # Desactivar
        
        # Aplicar
        import threading
        threading.Thread(
            target=self._apply_optimizations_thread,
            args=(reverted,),
            daemon=True
        ).start()
        
        self.show_toast("⏳ Revirtiendo...", "Restaurando configuración predeterminada")
    
    def show_toast(self, title: str, message: str):
        """Mostrar notificación toast (placeholder)"""
        log_info(f"TOAST: {title} - {message}")
        # TODO: Implementar toast notification con CTkMessagebox o similar
    
    def _on_alert_triggered(self, alert):
        """Callback cuando se dispara una alerta"""
        log_warning(f"Alerta: {alert.message}")
        
        # Actualizar UI de alertas si estamos en ese tab
        self.refresh_active_alerts()
        
        # Mostrar toast
        icon = "🔴" if alert.severity.value == "critical" else "⚠️"
        self.show_toast(f"{icon} Alerta", alert.message)
    
    def refresh_active_alerts(self):
        """Actualizar display de alertas activas"""
        if not self.alert_system:
            return
        
        try:
            # Limpiar container
            for widget in self.active_alerts_container.winfo_children():
                widget.destroy()
            
            # Obtener alertas activas
            active_alerts = self.alert_system.get_active_alerts()
            
            if not active_alerts:
                no_alerts_label = ctk.CTkLabel(
                    self.active_alerts_container,
                    text="✅ No hay alertas activas",
                    font=ctk.CTkFont(size=14),
                    text_color=TEXT_SUCCESS
                )
                no_alerts_label.pack(pady=20)
                return
            
            # Crear card para cada alerta
            for alert in active_alerts:
                card = ctk.CTkFrame(self.active_alerts_container, fg_color=BG_MAIN)
                card.pack(fill="x", pady=5)
                
                # Timestamp
                timestamp_str = alert.timestamp.strftime("%H:%M:%S")
                
                # Mensaje
                msg_label = ctk.CTkLabel(
                    card,
                    text=f"{timestamp_str} - {alert.message}",
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                msg_label.pack(side="left", padx=15, pady=10, fill="x", expand=True)
                
                # Botón resolver
                resolve_btn = ctk.CTkButton(
                    card,
                    text="✓ Resolver",
                    width=80,
                    height=30,
                    command=lambda a=alert: self.resolve_alert(a)
                )
                resolve_btn.pack(side="right", padx=10)
        
        except Exception as e:
            log_error(f"Error refrescando alertas: {e}")
    
    def resolve_alert(self, alert):
        """Resolver alerta manualmente"""
        if self.alert_system:
            self.alert_system.resolve_alert(alert)
            self.refresh_active_alerts()
            self.show_toast("✅ Alerta Resuelta", "Alerta marcada como resuelta")
    
    def apply_alert_thresholds(self):
        """Aplicar configuración de thresholds"""
        # TODO: Leer valores de los entries y aplicar
        self.show_toast("💾 Guardado", "Thresholds actualizados")
    
    def create_backup_now(self):
        """Crear backup inmediatamente"""
        if not self.backup_system:
            self.show_toast("Error", "Sistema de backups no disponible")
            return
        
        try:
            # Crear snapshot
            adapter = self.current_adapter
            description = f"Backup manual - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            snapshot = self.backup_system.create_snapshot(adapter, description)
            
            self.show_toast(
                "📸 Backup Creado",
                f"Snapshot: {snapshot.backup_id}"
            )
            
            # Actualizar lista
            self.refresh_backups_list()
        
        except Exception as e:
            log_error(f"Error creando backup: {e}")
            self.show_toast("❌ Error", f"No se pudo crear backup: {e}")
    
    def refresh_backups_list(self):
        """Actualizar lista de backups"""
        if not self.backup_system:
            return
        
        try:
            # Limpiar container
            for widget in self.backups_container.winfo_children():
                widget.destroy()
            
            # Obtener snapshots
            snapshots = self.backup_system.list_snapshots(limit=20)
            
            if not snapshots:
                no_backups_label = ctk.CTkLabel(
                    self.backups_container,
                    text="No hay backups disponibles",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
                no_backups_label.pack(pady=20)
                return
            
            # Crear card para cada backup
            for snapshot in snapshots:
                card = ctk.CTkFrame(self.backups_container, fg_color=BG_CARD)
                card.pack(fill="x", pady=5, padx=10)
                
                # Info container
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
                
                # ID y fecha
                id_label = ctk.CTkLabel(
                    info_frame,
                    text=f"📦 {snapshot.backup_id}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                id_label.pack(anchor="w")
                
                # Descripción
                desc_label = ctk.CTkLabel(
                    info_frame,
                    text=snapshot.description,
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                    anchor="w"
                )
                desc_label.pack(anchor="w")
                
                # Botones
                buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
                buttons_frame.pack(side="right", padx=10)
                
                restore_btn = ctk.CTkButton(
                    buttons_frame,
                    text="↩️ Restaurar",
                    width=100,
                    height=35,
                    command=lambda s=snapshot: self.restore_backup(s)
                )
                restore_btn.pack(side="left", padx=5)
                
                delete_btn = ctk.CTkButton(
                    buttons_frame,
                    text="🗑️",
                    width=40,
                    height=35,
                    fg_color="#ff6b6b",
                    hover_color="#d63031",
                    command=lambda s=snapshot: self.delete_backup(s)
                )
                delete_btn.pack(side="left", padx=5)
        
        except Exception as e:
            log_error(f"Error refrescando backups: {e}")
    
    def restore_backup(self, snapshot):
        """Restaurar backup"""
        if not self.backup_system:
            return
        
        try:
            success = self.backup_system.restore_snapshot(snapshot.backup_id, self.current_adapter)
            
            if success:
                self.show_toast(
                    "✅ Restaurado",
                    f"Configuración restaurada desde {snapshot.backup_id}"
                )
                # Refrescar DNS display
                self.refresh_dns_display()
            else:
                self.show_toast("❌ Error", "No se pudo restaurar backup")
        
        except Exception as e:
            log_error(f"Error restaurando backup: {e}")
            self.show_toast("❌ Error", str(e))
    
    def delete_backup(self, snapshot):
        """Eliminar backup"""
        if not self.backup_system:
            return
        
        try:
            success = self.backup_system.delete_snapshot(snapshot.backup_id)
            
            if success:
                self.show_toast("🗑️ Eliminado", f"Backup {snapshot.backup_id} eliminado")
                self.refresh_backups_list()
            else:
                self.show_toast("❌ Error", "No se pudo eliminar backup")
        
        except Exception as e:
            log_error(f"Error eliminando backup: {e}")
    
    def toggle_autofailover(self):
        """Alternar auto-failover DNS"""
        try:
            if self.autofailover_switch.get():
                # Habilitar
                from ..monitoring.dns_health import DNSHealthChecker
                from ..monitoring.auto_failover import AutoFailoverManager
                
                # Crear health checker
                self.dns_health_checker = DNSHealthChecker(check_interval=15)
                
                # Agregar todos los DNS servers de los tiers
                if self.adapter_manager:
                    tiers = self.adapter_manager.dns_fallback_tiers
                    for tier in tiers:
                        self.dns_health_checker.add_dns_server(tier.primary_dns)
                        if tier.secondary_dns:
                            self.dns_health_checker.add_dns_server(tier.secondary_dns)
                
                # Iniciar health checking
                self.dns_health_checker.start()
                
                # Crear auto-failover manager
                self.auto_failover_manager = AutoFailoverManager(
                    health_checker=self.dns_health_checker,
                    adapter_manager=self.adapter_manager,
                    cooldown_seconds=60
                )
                
                # Registrar callback para notificaciones
                self.auto_failover_manager.on_failover(self._on_dns_failover)
                
                # Iniciar auto-failover
                self.auto_failover_manager.start()
                
                # Actualizar UI
                self.health_status_label.configure(
                    text="Estado: ✅ Activo - Monitoreando DNS cada 15s",
                    text_color=TEXT_SUCCESS
                )
                
                self.show_toast(
                    "⚡ Auto-Failover Habilitado",
                    "DNS monitoreado automáticamente"
                )
                
                log_info("Auto-Failover DNS habilitado")
            
            else:
                # Deshabilitar
                if self.auto_failover_manager:
                    self.auto_failover_manager.stop()
                    self.auto_failover_manager = None
                
                if self.dns_health_checker:
                    self.dns_health_checker.stop()
                    self.dns_health_checker = None
                
                # Actualizar UI
                self.health_status_label.configure(
                    text="Estado: Deshabilitado",
                    text_color=TEXT_DISABLED
                )
                
                self.show_toast(
                    "Auto-Failover Deshabilitado",
                    "Monitoreo DNS detenido"
                )
                
                log_info("Auto-Failover DNS deshabilitado")
        
        except Exception as e:
            log_error(f"Error al toggle auto-failover: {e}")
            self.show_toast("Error", f"No se pudo cambiar auto-failover: {e}")
            # Revertir switch
            self.autofailover_switch.toggle()
    
    def _on_dns_failover(self, event):
        """Callback cuando ocurre un failover de DNS"""
        from ..utils.notifications import get_notification_manager
        
        # Notificación del sistema
        notif_mgr = get_notification_manager()
        if notif_mgr:
            notif_mgr.notify_dns_failover(
                from_tier=event.from_tier,
                to_tier=event.to_tier,
                tier_name=event.tier_name
            )
        
        # Actualizar display de DNS tiers
        self.refresh_dns_display()
        
        # Log
        log_info(f"DNS Failover: Tier {event.from_tier} → Tier {event.to_tier} ({event.tier_name})")
    
    def apply_all_optimizations(self):
        """Aplicar todas las optimizaciones"""
        if not self.is_admin:
            self.show_admin_required_dialog()
            return
        
        # Mostrar progreso
        self.show_progress_dialog("Aplicando optimizaciones...")
        
        # TODO: Ejecutar optimizaciones reales
        threading.Thread(target=self._apply_optimizations_thread, daemon=True).start()
    
    def _apply_optimizations_thread(self):
        """Thread para aplicar optimizaciones"""
        import time
        time.sleep(2)  # Simulación
        log_info("Optimizaciones aplicadas")
    
    def show_admin_required_dialog(self):
        """Mostrar diálogo de admin requerido"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Permisos Requeridos")
        dialog.geometry("400x200")
        
        label = ctk.CTkLabel(
            dialog,
            text="⚠️ Se requieren permisos de\nAdministrador",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label.pack(pady=30)
        
        restart_btn = ctk.CTkButton(
            dialog,
            text="Reiniciar como Admin",
            command=self.restart_as_admin
        )
        restart_btn.pack(pady=10)
    
    def show_progress_dialog(self, message: str):
        """Mostrar diálogo de progreso"""
        # TODO: Implementar
        pass
    
    def restart_as_admin(self):
        """Reiniciar como administrador"""
        import ctypes
        script = sys.argv[0]
        params = ' '.join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        self.quit()
    
    def on_closing(self):
        """Cleanup al cerrar la aplicación"""
        try:
            # Detener dashboard loop
            self._dashboard_active = False
            if self._dashboard_update_id:
                try:
                    self.after_cancel(self._dashboard_update_id)
                except Exception as e:
                    log_error(f"Error cancelando dashboard update: {e}")
            
            # Detener auto-failover
            if self.auto_failover_manager:
                try:
                    self.auto_failover_manager.stop()
                except Exception as e:
                    log_error(f"Error deteniendo auto-failover: {e}")
            
            # Detener DNS health checker
            if self.dns_health_checker:
                try:
                    self.dns_health_checker.stop()
                except Exception as e:
                    log_error(f"Error deteniendo DNS health checker: {e}")
            
            # Detener monitor de red
            if self.network_monitor:
                try:
                    self.network_monitor.stop()
                except Exception as e:
                    log_error(f"Error deteniendo network monitor: {e}")
            
            # Cerrar storage
            if self.storage:
                try:
                    self.storage.close()
                except Exception as e:
                    log_error(f"Error cerrando storage: {e}")
            
            log_info("NetBoozt cerrado correctamente")
        
        except Exception as e:
            log_error(f"Error en cleanup: {e}")
        
        finally:
            self.destroy()
    
    def _on_theme_changed(self, new_theme):
        """Callback cuando cambia el tema"""
        log_info(f"Tema cambiado a: {new_theme.value}")
        
        # Actualizar texto del botón si existe
        if hasattr(self, 'theme_toggle_btn'):
            new_text = "🌙 Modo Oscuro" if self.theme_manager.is_dark() else "☀️ Modo Claro"
            self.theme_toggle_btn.configure(text=new_text)
        
        # Re-aplicar configuración
        self.update()
    
    def toggle_theme(self):
        """Alternar entre dark/light mode"""
        if self.theme_manager:
            self.theme_manager.toggle()
            
            # Mostrar notificación
            new_theme = "Oscuro" if self.theme_manager.is_dark() else "Claro"
            self.show_toast(
                "🎨 Tema Cambiado",
                f"Modo {new_theme} activado"
            )
    
    def __del__(self):
        """Destructor - asegurar cleanup"""
        try:
            if hasattr(self, 'network_monitor') and self.network_monitor:
                self.network_monitor.stop()
        except Exception:
            pass
    
    def run(self):
        """Ejecutar aplicación"""
        self.mainloop()


if __name__ == "__main__":
    app = ModernNetBoozt()
    app.run()
