"""
NetBoozt - Documentation Tab
Navegador de documentación con índice y búsqueda

By LOUST (www.loust.pro)
"""

import customtkinter as ctk
from pathlib import Path
from typing import List, Dict
from .theme import *


class DocsTab(ctk.CTkFrame):
    """Tab de documentación con índice navegable"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=BG_MAIN)
        
        self.docs_path = Path(__file__).parent.parent.parent / "docs"
        self.current_doc = None
        
        self._create_ui()
        self._load_docs_index()
    
    def _create_ui(self):
        """Crear interfaz"""
        # Header
        header = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=RADIUS_LARGE, height=60)
        header.pack(fill="x", padx=PADDING_LARGE, pady=PADDING_LARGE)
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text=f"{ICONS['docs']} Documentación",
            font=ctk.CTkFont(size=FONT_SIZE_HEADER, weight="bold"),
            text_color=PRIMARY
        ).pack(side="left", padx=PADDING_LARGE)
        
        # Búsqueda
        self.search_entry = ctk.CTkEntry(
            header,
            placeholder_text="🔍 Buscar en documentación...",
            width=300,
            height=36,
            fg_color=BG_INPUT,
            border_color=BORDER_DEFAULT,
            border_width=1
        )
        self.search_entry.pack(side="right", padx=PADDING_LARGE)
        self.search_entry.bind("<KeyRelease>", self._on_search)
        
        # Container principal
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=(0, PADDING_LARGE))
        
        # Sidebar con índice (30%)
        self.sidebar = ctk.CTkScrollableFrame(
            content,
            fg_color=BG_CARD,
            corner_radius=RADIUS_LARGE,
            width=250,
            scrollbar_button_color=SCROLLBAR_COLOR,
            scrollbar_button_hover_color=SCROLLBAR_HOVER
        )
        self.sidebar.pack(side="left", fill="both", padx=(0, PADDING_NORMAL))
        self.sidebar.pack_propagate(False)
        
        # Área de contenido (70%)
        self.content_area = ctk.CTkScrollableFrame(
            content,
            fg_color=BG_CARD,
            corner_radius=RADIUS_LARGE,
            scrollbar_button_color=SCROLLBAR_COLOR,
            scrollbar_button_hover_color=SCROLLBAR_HOVER
        )
        self.content_area.pack(side="right", fill="both", expand=True)
    
    def _load_docs_index(self):
        """Cargar índice de documentación"""
        # Estructura de docs
        docs_structure = {
            "📘 Guía de Inicio": [
                ("Instalación", "installation.md"),
                ("Primeros Pasos", "getting-started.md"),
                ("Configuración", "configuration.md"),
            ],
            "⚡ Optimizaciones": [
                ("TCP Congestion Control", "optimizations/tcp.md"),
                ("RSS (Receive Side Scaling)", "optimizations/rss.md"),
                ("DNS Failover", "optimizations/dns.md"),
                ("Window Scaling", "optimizations/window-scaling.md"),
            ],
            "🌐 Red": [
                ("Adaptadores de Red", "network/adapters.md"),
                ("Métricas y Prioridades", "network/metrics.md"),
                ("Detección de Conectividad", "network/connectivity.md"),
            ],
            "🔧 Avanzado": [
                ("PowerShell Integration", "advanced/powershell.md"),
                ("Registry Tweaks", "advanced/registry.md"),
                ("Troubleshooting", "advanced/troubleshooting.md"),
            ],
            "📊 Dashboard": [
                ("Gráficas en Tiempo Real", "dashboard/realtime.md"),
                ("Métricas", "dashboard/metrics.md"),
                ("Exportar Datos", "dashboard/export.md"),
            ],
        }
        
        for category, items in docs_structure.items():
            # Categoría header
            cat_label = ctk.CTkLabel(
                self.sidebar,
                text=category,
                font=ctk.CTkFont(size=FONT_SIZE_NORMAL, weight="bold"),
                text_color=PRIMARY,
                anchor="w"
            )
            cat_label.pack(fill="x", padx=PADDING_NORMAL, pady=(PADDING_LARGE, PADDING_SMALL))
            
            # Items
            for title, file_path in items:
                self._add_doc_item(title, file_path)
        
        # Mostrar doc por defecto
        self._show_welcome()
    
    def _add_doc_item(self, title: str, file_path: str):
        """Agregar item al índice"""
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"  {title}",
            command=lambda: self._load_doc(file_path),
            fg_color="transparent",
            hover_color=BG_CARD_HOVER,
            text_color=TEXT_SECONDARY,
            anchor="w",
            height=32,
            corner_radius=RADIUS_SMALL
        )
        btn.pack(fill="x", padx=PADDING_SMALL, pady=2)
    
    def _load_doc(self, file_path: str):
        """Cargar documento"""
        # Limpiar contenido
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        doc_file = self.docs_path / file_path
        
        if not doc_file.exists():
            self._show_doc_not_found(file_path)
            return
        
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self._render_doc(content)
        except Exception as e:
            self._show_error(f"Error cargando {file_path}: {e}")
    
    def _show_welcome(self):
        """Mostrar pantalla de bienvenida"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        welcome = ctk.CTkFrame(self.content_area, fg_color="transparent")
        welcome.pack(fill="both", expand=True, padx=50, pady=50)
        
        ctk.CTkLabel(
            welcome,
            text="📚",
            font=ctk.CTkFont(size=80)
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            welcome,
            text="Centro de Documentación",
            font=ctk.CTkFont(size=FONT_SIZE_HERO, weight="bold"),
            text_color=PRIMARY
        ).pack(pady=10)
        
        ctk.CTkLabel(
            welcome,
            text="Selecciona un tema del índice para comenzar",
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=TEXT_SECONDARY
        ).pack()
        
        # Stats
        stats_frame = ctk.CTkFrame(welcome, fg_color=BG_SIDEBAR, corner_radius=RADIUS_LARGE)
        stats_frame.pack(pady=30, fill="x")
        
        stats = [
            ("📄", "15+", "Guías"),
            ("⚡", "13+", "Optimizaciones"),
            ("🔧", "50+", "Configuraciones"),
        ]
        
        for icon, value, label in stats:
            stat = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat.pack(side="left", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                stat,
                text=icon,
                font=ctk.CTkFont(size=40)
            ).pack()
            
            ctk.CTkLabel(
                stat,
                text=value,
                font=ctk.CTkFont(size=FONT_SIZE_HEADER, weight="bold"),
                text_color=PRIMARY
            ).pack()
            
            ctk.CTkLabel(
                stat,
                text=label,
                font=ctk.CTkFont(size=FONT_SIZE_SMALL),
                text_color=TEXT_SECONDARY
            ).pack()
    
    def _show_doc_not_found(self, file_path: str):
        """Mostrar mensaje de doc no encontrado"""
        error_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        error_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        ctk.CTkLabel(
            error_frame,
            text=ICONS['warning'],
            font=ctk.CTkFont(size=60),
            text_color=TEXT_WARNING
        ).pack(pady=20)
        
        ctk.CTkLabel(
            error_frame,
            text="Documento No Encontrado",
            font=ctk.CTkFont(size=FONT_SIZE_HEADER, weight="bold"),
            text_color=TEXT_WARNING
        ).pack()
        
        ctk.CTkLabel(
            error_frame,
            text=f"El archivo {file_path} aún no está disponible.",
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=TEXT_SECONDARY
        ).pack(pady=10)
        
        ctk.CTkLabel(
            error_frame,
            text="Esta sección estará disponible próximamente.",
            font=ctk.CTkFont(size=FONT_SIZE_SMALL),
            text_color=TEXT_DISABLED
        ).pack()
    
    def _show_error(self, message: str):
        """Mostrar error"""
        ctk.CTkLabel(
            self.content_area,
            text=f"{ICONS['error']} {message}",
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=TEXT_ERROR
        ).pack(pady=50)
    
    def _render_doc(self, content: str):
        """Renderizar documento markdown (simple)"""
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('# '):
                ctk.CTkLabel(
                    self.content_area,
                    text=line[2:],
                    font=ctk.CTkFont(size=FONT_SIZE_HERO, weight="bold"),
                    text_color=PRIMARY,
                    anchor="w"
                ).pack(fill="x", padx=20, pady=(20, 10))
            elif line.startswith('## '):
                ctk.CTkLabel(
                    self.content_area,
                    text=line[3:],
                    font=ctk.CTkFont(size=FONT_SIZE_HEADER, weight="bold"),
                    text_color=TEXT_PRIMARY,
                    anchor="w"
                ).pack(fill="x", padx=20, pady=(15, 5))
            elif line.strip():
                ctk.CTkLabel(
                    self.content_area,
                    text=line,
                    font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
                    text_color=TEXT_SECONDARY,
                    anchor="w",
                    wraplength=700
                ).pack(fill="x", padx=30, pady=2)
    
    def _on_search(self, event):
        """Manejar búsqueda"""
        query = self.search_entry.get().lower()
        
        if not query:
            return
        
        # TODO: Implementar búsqueda real
        # Por ahora solo muestra placeholder
        pass
