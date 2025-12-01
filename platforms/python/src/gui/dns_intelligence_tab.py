"""
NetBoozt - DNS Intelligence Tab
Tab de interfaz para análisis inteligente de DNS

Features:
- Ranking visual de DNS servers
- Métricas en tiempo real (ping, resolve time, uptime)
- Análisis histórico
- Selección automática del mejor DNS
"""

import customtkinter as ctk
import threading
from typing import Optional, Callable
from datetime import datetime

try:
    from ..monitoring.dns_intelligence import DNSIntelligence, DNSMetrics, get_dns_intelligence
    from ..utils.logger import log_info, log_error, log_warning
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from monitoring.dns_intelligence import DNSIntelligence, DNSMetrics, get_dns_intelligence
    from utils.logger import log_info, log_error, log_warning


class DNSServerCard(ctk.CTkFrame):
    """Card visual para mostrar un servidor DNS con sus métricas."""
    
    def __init__(self, parent, name: str, metrics: Optional[DNSMetrics] = None, 
                 rank: int = 0, on_select: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.name = name
        self.metrics = metrics
        self.rank = rank
        self.on_select = on_select
        
        self.configure(
            fg_color=("#f8f9fa", "#2b2b2b"),
            corner_radius=10,
            border_width=1,
            border_color=self._get_border_color()
        )
        
        self._create_widgets()
        self._update_display()
    
    def _get_border_color(self) -> str:
        """Color del borde según posición en ranking."""
        if self.rank == 1:
            return "#00d4aa"  # Verde - Mejor
        elif self.rank == 2:
            return "#ffc107"  # Amarillo - Segundo
        elif self.rank == 3:
            return "#fd7e14"  # Naranja - Tercero
        else:
            return ("#dee2e6", "#444444")
    
    def _create_widgets(self):
        """Crear widgets del card."""
        # Header con nombre y ranking
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        # Medalla de ranking
        rank_colors = {1: "#00d4aa", 2: "#ffc107", 3: "#fd7e14"}
        rank_color = rank_colors.get(self.rank, "#6c757d")
        
        self.rank_label = ctk.CTkLabel(
            header,
            text=f"#{self.rank}" if self.rank > 0 else "—",
            font=("Segoe UI", 14, "bold"),
            text_color=rank_color,
            width=35
        )
        self.rank_label.pack(side="left")
        
        self.name_label = ctk.CTkLabel(
            header,
            text=self.name,
            font=("Segoe UI", 14, "bold"),
            anchor="w"
        )
        self.name_label.pack(side="left", padx=5)
        
        # Score badge
        self.score_label = ctk.CTkLabel(
            header,
            text="—",
            font=("Segoe UI", 12),
            fg_color=("#e9ecef", "#3d3d3d"),
            corner_radius=5,
            width=60
        )
        self.score_label.pack(side="right", padx=5)
        
        # Métricas
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        # Ping
        ping_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        ping_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(
            ping_frame,
            text="Ping",
            font=("Segoe UI", 10),
            text_color=("#6c757d", "#a0a0a0")
        ).pack()
        
        self.ping_value = ctk.CTkLabel(
            ping_frame,
            text="—",
            font=("Segoe UI", 13, "bold")
        )
        self.ping_value.pack()
        
        # Resolve Time
        resolve_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        resolve_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(
            resolve_frame,
            text="Resolve",
            font=("Segoe UI", 10),
            text_color=("#6c757d", "#a0a0a0")
        ).pack()
        
        self.resolve_value = ctk.CTkLabel(
            resolve_frame,
            text="—",
            font=("Segoe UI", 13, "bold")
        )
        self.resolve_value.pack()
        
        # Uptime
        uptime_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        uptime_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(
            uptime_frame,
            text="Uptime",
            font=("Segoe UI", 10),
            text_color=("#6c757d", "#a0a0a0")
        ).pack()
        
        self.uptime_value = ctk.CTkLabel(
            uptime_frame,
            text="—",
            font=("Segoe UI", 13, "bold")
        )
        self.uptime_value.pack()
        
        # Status bar
        self.status_bar = ctk.CTkProgressBar(
            self,
            height=4,
            corner_radius=2,
            progress_color=self._get_border_color()
        )
        self.status_bar.pack(fill="x", padx=10, pady=(5, 0))
        self.status_bar.set(0)
        
        # Botón seleccionar
        self.select_btn = ctk.CTkButton(
            self,
            text="Usar este DNS",
            font=("Segoe UI", 11),
            height=28,
            fg_color=("#0078d4", "#0078d4"),
            hover_color=("#005a9e", "#005a9e"),
            command=self._on_select_click
        )
        self.select_btn.pack(fill="x", padx=10, pady=10)
    
    def _on_select_click(self):
        """Handler para click en botón seleccionar."""
        if self.on_select and self.metrics:
            self.on_select(self.metrics.server)
    
    def _update_display(self):
        """Actualizar display con métricas actuales."""
        if not self.metrics:
            return
        
        # Score
        self.score_label.configure(text=f"{self.metrics.score:.0f} pts")
        
        # Ping
        if self.metrics.avg_ping > 0:
            ping_color = "#00d4aa" if self.metrics.avg_ping < 30 else "#ffc107" if self.metrics.avg_ping < 100 else "#dc3545"
            self.ping_value.configure(text=f"{self.metrics.avg_ping:.0f}ms", text_color=ping_color)
        else:
            self.ping_value.configure(text="N/A", text_color=("#6c757d", "#a0a0a0"))
        
        # Resolve time
        if self.metrics.avg_resolve_time > 0:
            resolve_color = "#00d4aa" if self.metrics.avg_resolve_time < 100 else "#ffc107" if self.metrics.avg_resolve_time < 300 else "#dc3545"
            self.resolve_value.configure(text=f"{self.metrics.avg_resolve_time:.0f}ms", text_color=resolve_color)
        else:
            self.resolve_value.configure(text="N/A", text_color=("#6c757d", "#a0a0a0"))
        
        # Uptime
        uptime_color = "#00d4aa" if self.metrics.uptime_percent >= 99 else "#ffc107" if self.metrics.uptime_percent >= 90 else "#dc3545"
        self.uptime_value.configure(text=f"{self.metrics.uptime_percent:.0f}%", text_color=uptime_color)
        
        # Progress bar (score normalized to 100)
        self.status_bar.set(min(self.metrics.score / 100, 1.0))
    
    def update_metrics(self, metrics: DNSMetrics, rank: int):
        """Actualizar métricas y ranking."""
        self.metrics = metrics
        self.rank = rank
        
        # Actualizar color del borde
        self.configure(border_color=self._get_border_color())
        self.status_bar.configure(progress_color=self._get_border_color())
        
        # Actualizar ranking
        rank_colors = {1: "#00d4aa", 2: "#ffc107", 3: "#fd7e14"}
        rank_color = rank_colors.get(self.rank, "#6c757d")
        self.rank_label.configure(
            text=f"#{self.rank}" if self.rank > 0 else "—",
            text_color=rank_color
        )
        
        self._update_display()


class DNSIntelligenceTab(ctk.CTkScrollableFrame):
    """Tab principal para DNS Intelligence."""
    
    def __init__(self, parent, adapter_manager=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.adapter_manager = adapter_manager
        self.dns_intel = get_dns_intelligence()
        self.dns_cards: dict[str, DNSServerCard] = {}
        self.is_checking = False
        self._auto_refresh = True
        
        self._create_widgets()
        
        # Auto-iniciar monitoreo
        self._start_monitoring()
    
    def _create_widgets(self):
        """Crear widgets del tab."""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="🧠 DNS Intelligence",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Análisis inteligente y selección automática del mejor DNS",
            font=("Segoe UI", 12),
            text_color=("#6c757d", "#a0a0a0")
        ).pack(anchor="w")
        
        # Controles
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right")
        
        self.refresh_btn = ctk.CTkButton(
            controls,
            text="⟳ Analizar Ahora",
            font=("Segoe UI", 12),
            width=130,
            height=32,
            fg_color=("#0078d4", "#0078d4"),
            hover_color=("#005a9e", "#005a9e"),
            command=self._run_analysis
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        self.auto_select_btn = ctk.CTkButton(
            controls,
            text="✓ Auto-Seleccionar Mejor",
            font=("Segoe UI", 12),
            width=160,
            height=32,
            fg_color=("#00d4aa", "#00d4aa"),
            hover_color=("#00b894", "#00b894"),
            command=self._auto_select_best
        )
        self.auto_select_btn.pack(side="left", padx=5)
        
        # Status
        self.status_frame = ctk.CTkFrame(self, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8)
        self.status_frame.pack(fill="x", pady=(0, 15))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="⏳ Iniciando análisis de DNS...",
            font=("Segoe UI", 12),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=15, pady=10)
        
        # Container para cards
        self.cards_container = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True)
        
        # Summary section
        self.summary_frame = ctk.CTkFrame(self, fg_color=("#f8f9fa", "#2b2b2b"), corner_radius=10)
        self.summary_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkLabel(
            self.summary_frame,
            text="📊 Resumen",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.summary_text = ctk.CTkTextbox(
            self.summary_frame,
            height=100,
            font=("Consolas", 11),
            fg_color=("#ffffff", "#1a1a1a"),
            border_width=0
        )
        self.summary_text.pack(fill="x", padx=15, pady=(0, 10))
    
    def _start_monitoring(self):
        """Iniciar monitoreo en segundo plano."""
        def on_update(metrics: DNSMetrics):
            """Callback cuando se actualiza un DNS."""
            try:
                self.after(0, lambda: self._update_ui())
            except Exception as e:
                log_error("Error updating DNS intelligence UI", e)
        
        # Registrar callback
        self.dns_intel.on_update(on_update)
        
        # Iniciar monitoreo
        self.dns_intel.start_monitoring()
        
        log_info("DNS Intelligence monitoring started")
    
    def _run_analysis(self):
        """Ejecutar análisis manual."""
        if self.is_checking:
            return
        
        self.is_checking = True
        self.refresh_btn.configure(state="disabled", text="⏳ Analizando...")
        self.status_label.configure(text="🔍 Ejecutando análisis paralelo de todos los DNS...")
        
        def analyze():
            try:
                self.dns_intel.check_all_parallel()
                self.after(0, self._update_ui)
            except Exception as e:
                log_error("Error in DNS analysis", e)
                self.after(0, lambda: self.status_label.configure(
                    text=f"❌ Error en análisis: {e}"
                ))
            finally:
                self.is_checking = False
                self.after(0, lambda: self.refresh_btn.configure(
                    state="normal", 
                    text="⟳ Analizar Ahora"
                ))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def _update_ui(self):
        """Actualizar UI con datos actuales."""
        try:
            ranking = self.dns_intel.get_ranking()
            
            if not ranking:
                self.status_label.configure(text="⏳ Esperando datos de análisis...")
                return
            
            # Actualizar o crear cards
            for rank, (server, metrics) in enumerate(ranking, 1):
                name = metrics.name
                
                if name not in self.dns_cards:
                    # Crear nuevo card
                    card = DNSServerCard(
                        self.cards_container,
                        name=name,
                        metrics=metrics,
                        rank=rank,
                        on_select=self._on_dns_select
                    )
                    card.pack(fill="x", pady=5)
                    self.dns_cards[name] = card
                else:
                    # Actualizar card existente
                    self.dns_cards[name].update_metrics(metrics, rank)
            
            # Actualizar status
            best = self.dns_intel.get_best_dns()
            if best:
                self.status_label.configure(
                    text=f"✅ Mejor DNS: {best.name} ({best.server}) - Score: {best.score:.0f}"
                )
            else:
                self.status_label.configure(text="⚠️ No hay datos suficientes aún")
            
            # Actualizar summary
            summary = self.dns_intel.get_summary()
            self.summary_text.delete("1.0", "end")
            self.summary_text.insert("1.0", summary)
            
        except Exception as e:
            log_error("Error updating DNS Intelligence UI", e)
    
    def _on_dns_select(self, server: str):
        """Handler cuando se selecciona un DNS."""
        if not self.adapter_manager:
            log_warning("No adapter manager available")
            return
        
        try:
            log_info(f"User selected DNS: {server}")
            # Obtener adaptador activo
            adapters = self.adapter_manager.get_active_adapters()
            if adapters:
                adapter = adapters[0]
                # Cambiar DNS
                success = self.adapter_manager.change_dns(adapter.name, server, None)
                if success:
                    self.status_label.configure(
                        text=f"✅ DNS cambiado a {server} en {adapter.name}"
                    )
                else:
                    self.status_label.configure(
                        text=f"❌ Error al cambiar DNS a {server}"
                    )
            else:
                self.status_label.configure(
                    text="⚠️ No se encontró adaptador de red activo"
                )
        except Exception as e:
            log_error(f"Error changing DNS to {server}", e)
            self.status_label.configure(text=f"❌ Error: {e}")
    
    def _auto_select_best(self):
        """Seleccionar automáticamente el mejor DNS."""
        best = self.dns_intel.get_best_dns()
        if best:
            self._on_dns_select(best.server)
        else:
            self.status_label.configure(
                text="⚠️ No hay datos suficientes para seleccionar el mejor DNS"
            )
    
    def stop(self):
        """Detener monitoreo."""
        self._auto_refresh = False
        self.dns_intel.stop_monitoring()
        log_info("DNS Intelligence tab stopped")


# Test del módulo
if __name__ == "__main__":
    import customtkinter as ctk
    
    ctk.set_appearance_mode("dark")
    
    root = ctk.CTk()
    root.title("DNS Intelligence Test")
    root.geometry("800x700")
    
    tab = DNSIntelligenceTab(root)
    tab.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()
