"""
NetBoozt - README Tab
Visualizador de README con soporte multiidioma

By LOUST (www.loust.pro)
"""

import customtkinter as ctk
from pathlib import Path
import re
import sys
from typing import Optional
from .theme import *


class ReadmeTab(ctk.CTkScrollableFrame):
    """Tab para visualizar README con selector de idioma"""
    
    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=BG_MAIN,
            scrollbar_button_color=SCROLLBAR_COLOR,
            scrollbar_button_hover_color=SCROLLBAR_HOVER
        )
        
        self.current_language = 'es'
        
        # Detectar ruta base (frozen o desarrollo)
        if getattr(sys, 'frozen', False):
            # En modo frozen, README está junto al .exe
            self.readme_path = Path(sys.executable).parent
        else:
            # En desarrollo, README está en la raíz del proyecto
            self.readme_path = Path(__file__).parent.parent.parent
        
        self._create_ui()
        self._load_readme()
    
    def _create_ui(self):
        """Crear interfaz"""
        # Header con selector de idioma
        header = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=RADIUS_LARGE)
        header.pack(fill="x", padx=PADDING_LARGE, pady=(PADDING_LARGE, PADDING_NORMAL))
        
        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=PADDING_LARGE, pady=PADDING_NORMAL)
        
        ctk.CTkLabel(
            title_frame,
            text=f"{ICONS['readme']} README",
            font=ctk.CTkFont(size=FONT_SIZE_HEADER, weight="bold"),
            text_color=PRIMARY
        ).pack(side="left")
        
        # Selector de idioma
        lang_frame = ctk.CTkFrame(header, fg_color="transparent")
        lang_frame.pack(side="right", padx=PADDING_LARGE, pady=PADDING_NORMAL)
        
        ctk.CTkLabel(
            lang_frame,
            text=f"{ICONS['language']} ",
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL)
        ).pack(side="left", padx=(0, 5))
        
        self.lang_selector = ctk.CTkSegmentedButton(
            lang_frame,
            values=["🇪🇸 Español", "🇬🇧 English"],
            command=self._on_language_change,
            fg_color=BG_CARD,
            selected_color=PRIMARY,
            selected_hover_color=PRIMARY_HOVER,
            unselected_color=BG_INPUT,
            unselected_hover_color=BG_CARD_HOVER
        )
        self.lang_selector.pack(side="left")
        self.lang_selector.set("🇪🇸 Español")
        
        # Contenedor de contenido
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_NORMAL)
    
    def _on_language_change(self, value):
        """Cambiar idioma"""
        self.current_language = 'es' if 'Español' in value else 'en'
        self._load_readme()
    
    def _load_readme(self):
        """Cargar README en el idioma actual"""
        # Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            try:
                widget.destroy()
            except Exception:
                # Widget destruction can fail if already destroyed
                pass
        
        # Determinar archivo README
        if self.current_language == 'es':
            readme_file = self.readme_path / "README.md"
        else:
            readme_file = self.readme_path / "README_EN.md"
            if not readme_file.exists():
                readme_file = self.readme_path / "README.md"
        
        if not readme_file.exists():
            self._show_error("README no encontrado")
            return
        
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self._render_markdown(content)
        except Exception as e:
            self._show_error(f"Error cargando README: {e}")
    
    def _show_error(self, message):
        """Mostrar mensaje de error"""
        error_label = ctk.CTkLabel(
            self.content_frame,
            text=f"{ICONS['error']} {message}",
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=TEXT_ERROR
        )
        error_label.pack(pady=50)
    
    def _render_markdown(self, content: str):
        """Renderizar markdown simple"""
        lines = content.split('\n')
        
        for line in lines:
            line = line.rstrip()
            
            if not line:
                ctk.CTkLabel(self.content_frame, text="", height=5, fg_color="transparent").pack()
                continue
            
            # Headers
            if line.startswith('# '):
                self._add_header(line[2:], FONT_SIZE_HERO, PRIMARY)
            elif line.startswith('## '):
                self._add_header(line[3:], FONT_SIZE_HEADER, TEXT_PRIMARY)
            elif line.startswith('### '):
                self._add_header(line[4:], FONT_SIZE_LARGE, TEXT_SECONDARY)
            
            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                self._add_list_item(line[2:])
            elif re.match(r'^\d+\. ', line):
                self._add_list_item(line.split('. ', 1)[1], numbered=True)
            
            # Code blocks
            elif line.startswith('```'):
                continue  # Skip code block markers
            elif line.startswith('    '):
                self._add_code(line[4:])
            
            # Links
            elif '[' in line and '](' in line:
                self._add_link_text(line)
            
            # Bold/Italic
            elif '**' in line or '*' in line or '__' in line:
                self._add_formatted_text(line)
            
            # Normal text
            else:
                self._add_text(line)
    
    def _add_header(self, text: str, size: int, color: str):
        """Agregar header"""
        label = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(size=size, weight="bold"),
            text_color=color,
            anchor="w"
        )
        label.pack(fill="x", padx=PADDING_NORMAL, pady=(PADDING_LARGE, PADDING_SMALL))
    
    def _add_text(self, text: str):
        """Agregar texto normal"""
        if not text.strip():
            return
        
        label = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=TEXT_SECONDARY,
            anchor="w",
            wraplength=800
        )
        label.pack(fill="x", padx=PADDING_LARGE, pady=2)
    
    def _add_list_item(self, text: str, numbered: bool = False):
        """Agregar item de lista"""
        bullet = "  •" if not numbered else "  →"
        
        frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        frame.pack(fill="x", padx=PADDING_LARGE, pady=2)
        
        ctk.CTkLabel(
            frame,
            text=bullet,
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=PRIMARY,
            width=30,
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            frame,
            text=text,
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color=TEXT_SECONDARY,
            anchor="w",
            wraplength=750
        ).pack(side="left", fill="x", expand=True)
    
    def _add_code(self, text: str):
        """Agregar bloque de código"""
        label = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(family=FONT_FAMILY_MONO, size=FONT_SIZE_SMALL),
            text_color="#00ff88",
            fg_color=BG_INPUT,
            corner_radius=RADIUS_SMALL,
            anchor="w"
        )
        label.pack(fill="x", padx=PADDING_XL, pady=2)
    
    def _add_link_text(self, text: str):
        """Agregar texto con links"""
        # Simple rendering - just show as text with color
        label = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL),
            text_color="#00a8ff",
            anchor="w",
            wraplength=800
        )
        label.pack(fill="x", padx=PADDING_LARGE, pady=2)
    
    def _add_formatted_text(self, text: str):
        """Agregar texto formateado (bold/italic)"""
        # Strip formatting markers for simple display
        clean_text = text.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        
        label = ctk.CTkLabel(
            self.content_frame,
            text=clean_text,
            font=ctk.CTkFont(size=FONT_SIZE_NORMAL, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            wraplength=800
        )
        label.pack(fill="x", padx=PADDING_LARGE, pady=2)
