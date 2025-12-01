"""
NetBoozt - Gráficas Avanzadas con Zoom Temporal
Visualización mejorada de métricas con diferentes rangos de tiempo

By LOUST (www.loust.pro)
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator

try:
    from .theme import *
except ImportError:
    BG_MAIN = '#0a0a0a'
    BG_CARD = '#1a1a1a'
    PRIMARY = '#00d4aa'
    TEXT_PRIMARY = '#ffffff'


class TimeRange:
    """Rangos de tiempo predefinidos"""
    LAST_5_MIN = timedelta(minutes=5)
    LAST_15_MIN = timedelta(minutes=15)
    LAST_30_MIN = timedelta(minutes=30)
    LAST_1_HOUR = timedelta(hours=1)
    LAST_6_HOURS = timedelta(hours=6)
    LAST_24_HOURS = timedelta(hours=24)
    LAST_7_DAYS = timedelta(days=7)
    LAST_30_DAYS = timedelta(days=30)


class AdvancedGraph(ctk.CTkFrame):
    """Gráfica avanzada con zoom temporal"""
    
    def __init__(self, parent, title: str, ylabel: str, color: str = PRIMARY):
        super().__init__(parent, fg_color=BG_CARD, corner_radius=10)
        
        self.title_text = title
        self.ylabel = ylabel
        self.color = color
        self.current_range = TimeRange.LAST_30_MIN
        
        # Datos
        self.timestamps: List[datetime] = []
        self.values: List[float] = []
        self.max_data_points = 1000
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Crear interfaz"""
        # Header con título y controles
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        # Título
        title_label = ctk.CTkLabel(
            header,
            text=self.title_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")
        
        # Selector de rango
        self.range_menu = ctk.CTkOptionMenu(
            header,
            values=["5 min", "15 min", "30 min", "1 hora", "6 horas", "24 horas", "7 días"],
            command=self.on_range_changed,
            width=120,
            font=ctk.CTkFont(size=12)
        )
        self.range_menu.set("30 min")
        self.range_menu.pack(side="right", padx=5)
        
        # Figura de matplotlib
        self.figure = Figure(figsize=(8, 4), facecolor=BG_CARD, edgecolor=BG_CARD)
        self.ax = self.figure.add_subplot(111)
        
        # Estilo oscuro
        self.ax.set_facecolor(BG_MAIN)
        self.ax.spines['bottom'].set_color(TEXT_PRIMARY)
        self.ax.spines['top'].set_color(BG_CARD)
        self.ax.spines['right'].set_color(BG_CARD)
        self.ax.spines['left'].set_color(TEXT_PRIMARY)
        self.ax.tick_params(axis='x', colors=TEXT_PRIMARY, labelsize=9)
        self.ax.tick_params(axis='y', colors=TEXT_PRIMARY, labelsize=9)
        self.ax.set_ylabel(self.ylabel, color=TEXT_PRIMARY, fontsize=10)
        self.ax.grid(True, alpha=0.1, color=TEXT_PRIMARY)
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Línea inicial vacía
        self.line, = self.ax.plot([], [], color=self.color, linewidth=2)
    
    def add_data_point(self, timestamp: datetime, value: float):
        """Agregar punto de datos"""
        self.timestamps.append(timestamp)
        self.values.append(value)
        
        # Mantener tamaño controlado
        if len(self.timestamps) > self.max_data_points:
            self.timestamps = self.timestamps[-self.max_data_points:]
            self.values = self.values[-self.max_data_points:]
        
        # Actualizar gráfica
        self.update_plot()
    
    def on_range_changed(self, selected: str):
        """Cambiar rango temporal"""
        range_map = {
            "5 min": TimeRange.LAST_5_MIN,
            "15 min": TimeRange.LAST_15_MIN,
            "30 min": TimeRange.LAST_30_MIN,
            "1 hora": TimeRange.LAST_1_HOUR,
            "6 horas": TimeRange.LAST_6_HOURS,
            "24 horas": TimeRange.LAST_24_HOURS,
            "7 días": TimeRange.LAST_7_DAYS
        }
        
        self.current_range = range_map.get(selected, TimeRange.LAST_30_MIN)
        self.update_plot()
    
    def update_plot(self):
        """Actualizar gráfica con datos filtrados por rango"""
        if not self.timestamps:
            return
        
        # Filtrar datos por rango temporal
        now = datetime.now()
        cutoff = now - self.current_range
        
        filtered_times = []
        filtered_values = []
        
        for ts, val in zip(self.timestamps, self.values):
            if ts >= cutoff:
                filtered_times.append(ts)
                filtered_values.append(val)
        
        # Actualizar línea
        self.line.set_data(filtered_times, filtered_values)
        
        # Ajustar ejes
        if filtered_times:
            self.ax.set_xlim(cutoff, now)
            
            if filtered_values:
                y_min = min(filtered_values)
                y_max = max(filtered_values)
                y_padding = (y_max - y_min) * 0.1 if y_max > y_min else 1
                self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
            
            # Formatear eje X según rango
            if self.current_range <= TimeRange.LAST_1_HOUR:
                # Minutos
                self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
                self.ax.xaxis.set_major_locator(MinuteLocator(interval=5))
            elif self.current_range <= TimeRange.LAST_24_HOURS:
                # Horas
                self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
                self.ax.xaxis.set_major_locator(HourLocator(interval=2))
            else:
                # Días
                self.ax.xaxis.set_major_formatter(DateFormatter('%d/%m'))
        
        # Rotar labels
        self.figure.autofmt_xdate(rotation=45)
        
        # Redibujar
        self.canvas.draw()
    
    def clear(self):
        """Limpiar datos"""
        self.timestamps.clear()
        self.values.clear()
        self.line.set_data([], [])
        self.canvas.draw()


class AdvancedGraphsTab(ctk.CTkScrollableFrame):
    """Tab con gráficas avanzadas"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="📈 Gráficas Avanzadas",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Grid de gráficas
        graphs_container = ctk.CTkFrame(self, fg_color="transparent")
        graphs_container.pack(fill="both", expand=True)
        
        # Configurar grid 2x2
        graphs_container.grid_columnconfigure(0, weight=1)
        graphs_container.grid_columnconfigure(1, weight=1)
        graphs_container.grid_rowconfigure(0, weight=1)
        graphs_container.grid_rowconfigure(1, weight=1)
        
        # Gráfica de Download
        self.download_graph = AdvancedGraph(
            graphs_container,
            "Velocidad de Descarga",
            "Mbps",
            color="#00d4aa"
        )
        self.download_graph.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Gráfica de Upload
        self.upload_graph = AdvancedGraph(
            graphs_container,
            "Velocidad de Subida",
            "Mbps",
            color="#6c5ce7"
        )
        self.upload_graph.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Gráfica de Latencia
        self.latency_graph = AdvancedGraph(
            graphs_container,
            "Latencia",
            "ms",
            color="#fdcb6e"
        )
        self.latency_graph.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Gráfica de Packet Loss
        self.packet_loss_graph = AdvancedGraph(
            graphs_container,
            "Pérdida de Paquetes",
            "%",
            color="#ff6b6b"
        )
        self.packet_loss_graph.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    
    def update_graphs(self, timestamp: datetime, metrics: Dict):
        """Actualizar todas las gráficas"""
        if 'download_mbps' in metrics:
            self.download_graph.add_data_point(timestamp, metrics['download_mbps'])
        
        if 'upload_mbps' in metrics:
            self.upload_graph.add_data_point(timestamp, metrics['upload_mbps'])
        
        if 'latency_ms' in metrics:
            self.latency_graph.add_data_point(timestamp, metrics['latency_ms'])
        
        if 'packet_loss' in metrics:
            self.packet_loss_graph.add_data_point(timestamp, metrics['packet_loss'])


if __name__ == "__main__":
    # Test
    import random
    
    app = ctk.CTk()
    app.geometry("1200x800")
    
    tab = AdvancedGraphsTab(app)
    tab.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Simular datos
    def simulate_data():
        now = datetime.now()
        metrics = {
            'download_mbps': random.uniform(50, 100),
            'upload_mbps': random.uniform(10, 20),
            'latency_ms': random.uniform(10, 50),
            'packet_loss': random.uniform(0, 2)
        }
        tab.update_graphs(now, metrics)
        
        app.after(1000, simulate_data)
    
    simulate_data()
    
    app.mainloop()
