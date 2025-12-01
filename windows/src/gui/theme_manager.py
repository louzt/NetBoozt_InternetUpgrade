"""
NetBoozt - Theme Manager
Sistema de temas dinámico (Dark/Light mode)

By LOUST (www.loust.pro)
"""

from typing import Dict, Optional
from enum import Enum
import customtkinter as ctk


class ThemeMode(Enum):
    """Modos de tema"""
    DARK = "dark"
    LIGHT = "light"


class ThemeManager:
    """Gestor de temas dinámico"""
    
    THEMES = {
        'dark': {
            # Backgrounds
            'BG_MAIN': '#0a0a0a',
            'BG_CARD': '#1a1a1a',
            'BG_HOVER': '#2a2a2a',
            'BG_SIDEBAR': '#141414',
            
            # Colors
            'PRIMARY': '#00d4aa',
            'SECONDARY': '#6c5ce7',
            'ACCENT': '#fd79a8',
            
            # Text
            'TEXT_PRIMARY': '#ffffff',
            'TEXT_SECONDARY': '#a0a0a0',
            'TEXT_DISABLED': '#606060',
            
            # Semantic
            'TEXT_SUCCESS': '#00d4aa',
            'TEXT_WARNING': '#fdcb6e',
            'TEXT_ERROR': '#ff6b6b',
            
            # Borders
            'BORDER_DEFAULT': '#2a2a2a',
            'BORDER_FOCUS': '#00d4aa',
            
            # Radius
            'RADIUS_LARGE': 15,
            'RADIUS_MEDIUM': 10,
            'RADIUS_SMALL': 6,
        },
        'light': {
            # Backgrounds
            'BG_MAIN': '#ffffff',
            'BG_CARD': '#f5f5f5',
            'BG_HOVER': '#e8e8e8',
            'BG_SIDEBAR': '#fafafa',
            
            # Colors
            'PRIMARY': '#00b894',
            'SECONDARY': '#6c5ce7',
            'ACCENT': '#fd79a8',
            
            # Text
            'TEXT_PRIMARY': '#1a1a1a',
            'TEXT_SECONDARY': '#606060',
            'TEXT_DISABLED': '#a0a0a0',
            
            # Semantic
            'TEXT_SUCCESS': '#00b894',
            'TEXT_WARNING': '#e17055',
            'TEXT_ERROR': '#d63031',
            
            # Borders
            'BORDER_DEFAULT': '#e0e0e0',
            'BORDER_FOCUS': '#00b894',
            
            # Radius
            'RADIUS_LARGE': 15,
            'RADIUS_MEDIUM': 10,
            'RADIUS_SMALL': 6,
        }
    }
    
    def __init__(self, initial_theme: ThemeMode = ThemeMode.DARK):
        self.current_theme = initial_theme
        self._callbacks = []
        
        # Aplicar tema inicial
        self.apply_theme(initial_theme)
    
    def get(self, key: str) -> any:
        """Obtener valor del tema actual"""
        theme_dict = self.THEMES[self.current_theme.value]
        return theme_dict.get(key)
    
    def get_all(self) -> Dict:
        """Obtener todos los valores del tema actual"""
        return self.THEMES[self.current_theme.value].copy()
    
    def apply_theme(self, theme: ThemeMode):
        """Aplicar tema"""
        self.current_theme = theme
        
        # Cambiar apariencia de CustomTkinter
        ctk.set_appearance_mode(theme.value)
        
        # Notificar callbacks
        for callback in self._callbacks:
            try:
                callback(theme)
            except Exception as e:
                print(f"Error en theme callback: {e}")
    
    def toggle(self):
        """Alternar entre dark/light"""
        new_theme = ThemeMode.LIGHT if self.current_theme == ThemeMode.DARK else ThemeMode.DARK
        self.apply_theme(new_theme)
    
    def on_theme_change(self, callback):
        """Registrar callback para cambios de tema"""
        self._callbacks.append(callback)
    
    def is_dark(self) -> bool:
        """Verificar si está en modo oscuro"""
        return self.current_theme == ThemeMode.DARK
    
    def is_light(self) -> bool:
        """Verificar si está en modo claro"""
        return self.current_theme == ThemeMode.LIGHT


# Singleton global
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Obtener instancia global del theme manager"""
    global _theme_manager
    
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    
    return _theme_manager


def init_theme(theme: ThemeMode = ThemeMode.DARK) -> ThemeManager:
    """Inicializar theme manager"""
    global _theme_manager
    _theme_manager = ThemeManager(initial_theme=theme)
    return _theme_manager


# Exportar constantes del tema actual (para compatibilidad)
def _get_theme_constants():
    """Helper para obtener constantes del tema"""
    tm = get_theme_manager()
    return tm.get_all()


# Actualizar dinámicamente al importar
def __getattr__(name):
    """Magic method para acceder a constantes del tema"""
    tm = get_theme_manager()
    value = tm.get(name)
    
    if value is not None:
        return value
    
    raise AttributeError(f"Constante de tema '{name}' no encontrada")


if __name__ == "__main__":
    # Test
    tm = ThemeManager()
    
    print(f"Tema actual: {tm.current_theme.value}")
    print(f"BG_MAIN (dark): {tm.get('BG_MAIN')}")
    
    # Cambiar a light
    tm.apply_theme(ThemeMode.LIGHT)
    print(f"\nTema actual: {tm.current_theme.value}")
    print(f"BG_MAIN (light): {tm.get('BG_MAIN')}")
    
    # Toggle
    tm.toggle()
    print(f"\nDespués de toggle: {tm.current_theme.value}")
