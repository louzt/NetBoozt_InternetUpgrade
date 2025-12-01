"""
NetBoozt - Dashboard en Tiempo Real
Gráficas de métricas de red con matplotlib embebido

By LOUST (www.loust.pro)
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import deque
import threading


class RealtimeGraph(ctk.CTkFrame):
    """Gráfica en tiempo real embebida en CTk"""
    
    def __init__(self, master, title: str = "", ylabel: str = "", 
                 max_points: int = 60, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title_text = title
        self.ylabel = ylabel
        self.max_points = max_points
        
        # Datos
        self.timestamps: deque = deque(maxlen=max_points)
        self.data_series: Dict[str, deque] = {}
        
        # Importar theme
        from .theme import BG_CARD, BORDER_DEFAULT, TEXT_PRIMARY, TEXT_SECONDARY
        
        # Crear figura de matplotlib con tema oscuro
        self.fig = Figure(figsize=(6, 3), dpi=100, facecolor=BG_CARD)
        self.ax = self.fig.add_subplot(111)
        
        # Estilo oscuro
        self.ax.set_facecolor(BG_CARD)
        self.ax.spines['bottom'].set_color(BORDER_DEFAULT)
        self.ax.spines['top'].set_color(BORDER_DEFAULT)
        self.ax.spines['left'].set_color(BORDER_DEFAULT)
        self.ax.spines['right'].set_color(BORDER_DEFAULT)
        self.ax.tick_params(colors=TEXT_SECONDARY)
        self.ax.xaxis.label.set_color(TEXT_SECONDARY)
        self.ax.yaxis.label.set_color(TEXT_SECONDARY)
        self.ax.title.set_color(TEXT_PRIMARY)
        
        # Configurar gráfica
        self.ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.set_xlabel("Tiempo", fontsize=10)
        self.ax.grid(True, alpha=0.2, linestyle='--', color='#404040')
        
        # Canvas de tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Lines (se crean dinámicamente)
        self.lines: Dict[str, plt.Line2D] = {}
    
    def add_series(self, name: str, color: str = '#1f77b4', label: str = None):
        """Agregar serie de datos"""
        if name not in self.data_series:
            self.data_series[name] = deque(maxlen=self.max_points)
            
            # Crear línea
            line, = self.ax.plot([], [], color=color, linewidth=2, 
                                label=label or name, alpha=0.8)
            self.lines[name] = line
            
            # Actualizar leyenda
            if len(self.lines) > 1:
                from .theme import BG_HOVER, BORDER_DEFAULT, TEXT_SECONDARY
                self.ax.legend(loc='upper left', framealpha=0.7, 
                              facecolor=BG_HOVER, edgecolor=BORDER_DEFAULT,
                              labelcolor=TEXT_SECONDARY)
    
    def update(self, timestamp: datetime, data: Dict[str, float]):
        """
        Actualizar gráfica con nuevos datos
        
        Args:
            timestamp: Timestamp del dato
            data: Dict con {serie_name: value}
        """
        self.timestamps.append(timestamp)
        
        # Actualizar cada serie
        for name, value in data.items():
            if name not in self.data_series:
                # Auto-crear serie
                colors = ['#00a8ff', '#00ff88', '#ffd700', '#ff6b6b', '#a55eea']
                color = colors[len(self.data_series) % len(colors)]
                self.add_series(name, color)
            
            self.data_series[name].append(value)
        
        # Redibujar
        self._redraw()
    
    def _redraw(self):
        """Redibujar gráfica"""
        # Actualizar cada línea
        for name, line in self.lines.items():
            if name in self.data_series:
                # Convertir timestamps a segundos relativos
                if self.timestamps:
                    base_time = self.timestamps[0]
                    x_data = [(t - base_time).total_seconds() for t in self.timestamps]
                    y_data = list(self.data_series[name])
                    
                    # Rellenar con None si faltan datos
                    while len(y_data) < len(x_data):
                        y_data.insert(0, 0)
                    
                    line.set_data(x_data, y_data)
        
        # Ajustar ejes
        if self.timestamps:
            self.ax.relim()
            self.ax.autoscale_view()
            
            # Formatear eje X (segundos)
            self.ax.set_xlabel(f"Tiempo (últimos {self.max_points}s)", fontsize=10)
        
        # Redibujar canvas
        self.canvas.draw_idle()
    
    def clear(self):
        """Limpiar datos"""
        self.timestamps.clear()
        for series in self.data_series.values():
            series.clear()
        self._redraw()


class NetworkDashboard(ctk.CTkScrollableFrame):
    """Dashboard completo con múltiples gráficas"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Importar theme
        from .theme import TEXT_PRIMARY, BG_CARD, BG_HOVER, PRIMARY, FONT_FAMILY, FONT_SIZE_HEADER
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="📊 Dashboard en Tiempo Real",
            font=(FONT_FAMILY, FONT_SIZE_HEADER, "bold"),
            text_color=TEXT_PRIMARY
        )
        title.pack(pady=(10, 20))
        
        # Container de gráficas (2 columnas)
        graphs_container = ctk.CTkFrame(self, fg_color="transparent")
        graphs_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        graphs_container.grid_columnconfigure((0, 1), weight=1)
        graphs_container.grid_rowconfigure((0, 1), weight=1)
        
        # Gráfica 1: Velocidad de descarga/subida
        self.speed_graph = RealtimeGraph(
            graphs_container,
            title="Velocidad de Red",
            ylabel="Mbps",
            max_points=60,
            fg_color=BG_CARD
        )
        self.speed_graph.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.speed_graph.add_series("download", "#00a8ff", "Descarga")
        self.speed_graph.add_series("upload", "#00ff88", "Subida")
        
        # Gráfica 2: Latencia
        self.latency_graph = RealtimeGraph(
            graphs_container,
            title="Latencia",
            ylabel="ms",
            max_points=60,
            fg_color=BG_CARD
        )
        self.latency_graph.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.latency_graph.add_series("ping", "#ffd700", "Ping")
        
        # Gráfica 3: Paquetes
        self.packets_graph = RealtimeGraph(
            graphs_container,
            title="Paquetes",
            ylabel="paquetes/s",
            max_points=60,
            fg_color=BG_CARD
        )
        self.packets_graph.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.packets_graph.add_series("sent", "#a55eea", "Enviados")
        self.packets_graph.add_series("recv", "#00d2d3", "Recibidos")
        
        # Gráfica 4: Errores y pérdidas
        self.errors_graph = RealtimeGraph(
            graphs_container,
            title="Errores y Pérdidas",
            ylabel="paquetes",
            max_points=60,
            fg_color=BG_CARD
        )
        self.errors_graph.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.errors_graph.add_series("errors", "#ff6b6b", "Errores")
        self.errors_graph.add_series("drops", "#ff9ff3", "Pérdidas")
        
        # Estadísticas en vivo
        stats_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8)
        stats_frame.pack(fill="x", padx=10, pady=15)
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📈 Estadísticas Actuales",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=TEXT_PRIMARY
        )
        stats_title.pack(pady=10)
        
        # Grid de stats
        self.stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        self.stats_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        self.stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stats labels
        self.stat_labels = {}
        stats_config = [
            ("avg_download", "📥 Descarga Prom.", "0.0 Mbps"),
            ("avg_upload", "📤 Subida Prom.", "0.0 Mbps"),
            ("peak_download", "⚡ Descarga Máx.", "0.0 Mbps"),
            ("peak_upload", "⚡ Subida Máx.", "0.0 Mbps"),
            ("avg_latency", "🏓 Latencia Prom.", "0 ms"),
            ("packet_loss", "❌ Pérdida Paquetes", "0%"),
            ("total_errors", "⚠️ Errores Totales", "0"),
            ("uptime", "⏱️ Tiempo Activo", "00:00:00")
        ]
        
        for i, (key, label_text, default_value) in enumerate(stats_config):
            row = i // 4
            col = i % 4
            
            from .theme import TEXT_DISABLED
            
            stat_container = ctk.CTkFrame(self.stats_grid, fg_color=BG_HOVER, corner_radius=6)
            stat_container.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            label = ctk.CTkLabel(
                stat_container,
                text=label_text,
                font=(FONT_FAMILY, 10),
                text_color=TEXT_DISABLED
            )
            label.pack(pady=(8, 2))
            
            value = ctk.CTkLabel(
                stat_container,
                text=default_value,
                font=(FONT_FAMILY, 14, "bold"),
                text_color=PRIMARY
            )
            value.pack(pady=(0, 8))
            
            self.stat_labels[key] = value
        
        # Tiempo de inicio
        self.start_time = datetime.now()
    
    def update_graphs(self, timestamp: datetime, metrics: Dict[str, float]):
        """
        Actualizar todas las gráficas
        
        Args:
            timestamp: Timestamp del dato
            metrics: Dict con métricas {
                'download_mbps': float,
                'upload_mbps': float,
                'latency_ms': float,
                'packets_sent_per_sec': float,
                'packets_recv_per_sec': float,
                'errors_per_sec': float,
                'drops_per_sec': float
            }
        """
        # Actualizar gráfica de velocidad
        self.speed_graph.update(timestamp, {
            'download': metrics.get('download_mbps', 0),
            'upload': metrics.get('upload_mbps', 0)
        })
        
        # Actualizar latencia
        if 'latency_ms' in metrics:
            self.latency_graph.update(timestamp, {
                'ping': metrics['latency_ms']
            })
        
        # Actualizar paquetes
        self.packets_graph.update(timestamp, {
            'sent': metrics.get('packets_sent_per_sec', 0),
            'recv': metrics.get('packets_recv_per_sec', 0)
        })
        
        # Actualizar errores
        self.errors_graph.update(timestamp, {
            'errors': metrics.get('errors_per_sec', 0),
            'drops': metrics.get('drops_per_sec', 0)
        })
    
    def update_stats(self, stats: Dict[str, any]):
        """
        Actualizar estadísticas
        
        Args:
            stats: Dict con estadísticas {
                'avg_download_mbps': float,
                'avg_upload_mbps': float,
                'peak_download_mbps': float,
                'peak_upload_mbps': float,
                'avg_latency_ms': float,
                'packet_loss_percent': float,
                'total_errors': int
            }
        """
        # Actualizar labels
        if 'avg_download_mbps' in stats:
            self.stat_labels['avg_download'].configure(
                text=f"{stats['avg_download_mbps']:.1f} Mbps"
            )
        
        if 'avg_upload_mbps' in stats:
            self.stat_labels['avg_upload'].configure(
                text=f"{stats['avg_upload_mbps']:.1f} Mbps"
            )
        
        if 'peak_download_mbps' in stats:
            self.stat_labels['peak_download'].configure(
                text=f"{stats['peak_download_mbps']:.1f} Mbps"
            )
        
        if 'peak_upload_mbps' in stats:
            self.stat_labels['peak_upload'].configure(
                text=f"{stats['peak_upload_mbps']:.1f} Mbps"
            )
        
        if 'avg_latency_ms' in stats:
            self.stat_labels['avg_latency'].configure(
                text=f"{stats['avg_latency_ms']:.0f} ms"
            )
        
        if 'packet_loss_percent' in stats:
            self.stat_labels['packet_loss'].configure(
                text=f"{stats['packet_loss_percent']:.2f}%"
            )
        
        if 'total_errors' in stats:
            self.stat_labels['total_errors'].configure(
                text=f"{stats['total_errors']}"
            )
        
        # Uptime
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        seconds = int(uptime.total_seconds() % 60)
        self.stat_labels['uptime'].configure(
            text=f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )
    
    def clear_all(self):
        """Limpiar todas las gráficas"""
        self.speed_graph.clear()
        self.latency_graph.clear()
        self.packets_graph.clear()
        self.errors_graph.clear()
        
        # Resetear tiempo
        self.start_time = datetime.now()
