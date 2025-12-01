"""
System Tray Icon - Icono en la bandeja del sistema

Este módulo implementa un icono en la bandeja del sistema (al lado del reloj)
que permite:
1. Ver estado rápido de la conexión
2. Acceder a opciones comunes
3. Abrir/cerrar la ventana principal
4. Salir de la aplicación

Requiere: pystray, Pillow

By LOUST (www.loust.pro)
"""

import threading
from typing import Optional, Callable, List
from dataclasses import dataclass
import sys
from pathlib import Path

try:
    import pystray
    from pystray import MenuItem as Item, Menu
    from PIL import Image, ImageDraw, ImageFont
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    print("Warning: pystray not installed. System tray icon disabled.")
    print("Install with: pip install pystray pillow")


@dataclass
class TrayMenuAction:
    """Acción del menú del tray."""
    label: str
    callback: Callable
    enabled: bool = True
    checked: bool = False
    is_separator: bool = False
    submenu: Optional[List['TrayMenuAction']] = None


class SystemTrayIcon:
    """
    Icono en la bandeja del sistema con menú contextual.
    """
    
    def __init__(
        self,
        title: str = "NetBoozt",
        icon_path: Optional[Path] = None,
        on_click: Optional[Callable] = None,
        on_double_click: Optional[Callable] = None,
    ):
        self.title = title
        self.icon_path = icon_path
        self.on_click = on_click
        self.on_double_click = on_double_click
        
        self._icon: Optional['pystray.Icon'] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._menu_items: List[TrayMenuAction] = []
        
        # Estado para mostrar en icono
        self._status = "normal"  # normal, warning, error, disabled
        self._tooltip = title
        
        # Callbacks
        self._on_show_window: Optional[Callable] = None
        self._on_hide_window: Optional[Callable] = None
        self._on_quit: Optional[Callable] = None
    
    def _create_icon_image(self, size: int = 64) -> 'Image.Image':
        """
        Crea imagen del icono dinámicamente.
        Color basado en estado.
        """
        # Colores según estado
        colors = {
            "normal": "#00d4aa",    # Verde LOUST
            "warning": "#ffaa00",   # Amarillo
            "error": "#ff4444",     # Rojo
            "disabled": "#666666",  # Gris
        }
        
        color = colors.get(self._status, colors["normal"])
        
        # Crear imagen
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Dibujar círculo de fondo
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color
        )
        
        # Dibujar "N" en el centro
        try:
            # Intentar usar fuente del sistema
            font_size = size // 2
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        
        text = "N"
        # Centrar texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - 2
        
        draw.text((x, y), text, fill="white", font=font)
        
        return image
    
    def _load_icon_image(self) -> 'Image.Image':
        """Carga imagen del icono desde archivo o crea una."""
        if self.icon_path and self.icon_path.exists():
            try:
                return Image.open(self.icon_path)
            except Exception:
                pass
        
        return self._create_icon_image()
    
    def _build_menu(self) -> 'Menu':
        """Construye el menú del tray."""
        items = []
        
        # Header
        items.append(Item(
            f"NetBoozt - {self._status.title()}",
            lambda: None,
            enabled=False
        ))
        items.append(Item("─" * 20, lambda: None, enabled=False))
        
        # Mostrar/Ocultar ventana
        items.append(Item(
            "Mostrar ventana",
            self._handle_show_window
        ))
        
        items.append(Item("─" * 20, lambda: None, enabled=False))
        
        # Acciones rápidas
        items.append(Item(
            "DNS",
            Menu(
                Item("Usar Cloudflare (1.1.1.1)", lambda: self._quick_dns("cloudflare")),
                Item("Usar Google (8.8.8.8)", lambda: self._quick_dns("google")),
                Item("Usar Quad9 (9.9.9.9)", lambda: self._quick_dns("quad9")),
                Item("─" * 15, lambda: None, enabled=False),
                Item("Auto (Mejor DNS)", lambda: self._quick_dns("auto")),
                Item("Reset a DHCP", lambda: self._quick_dns("dhcp")),
            )
        ))
        
        items.append(Item(
            "Optimizaciones",
            Menu(
                Item("Aplicar Balanceado", lambda: self._quick_optimize("balanced")),
                Item("Aplicar Agresivo", lambda: self._quick_optimize("aggressive")),
                Item("─" * 15, lambda: None, enabled=False),
                Item("Restaurar defaults", lambda: self._quick_optimize("reset")),
            )
        ))
        
        items.append(Item(
            "Diagnóstico rápido",
            self._handle_quick_diagnostic
        ))
        
        items.append(Item("─" * 20, lambda: None, enabled=False))
        
        # Opciones
        items.append(Item(
            "Iniciar con Windows",
            self._toggle_autostart,
            checked=lambda item: self._is_autostart_enabled()
        ))
        
        items.append(Item(
            "Minimizar a tray al cerrar",
            self._toggle_minimize_to_tray,
            checked=lambda item: self._is_minimize_to_tray()
        ))
        
        items.append(Item("─" * 20, lambda: None, enabled=False))
        
        # Salir
        items.append(Item(
            "Salir",
            self._handle_quit
        ))
        
        return Menu(*items)
    
    def _handle_show_window(self):
        """Maneja click en mostrar ventana."""
        if self._on_show_window:
            self._on_show_window()
    
    def _handle_quit(self):
        """Maneja salir de la aplicación."""
        if self._on_quit:
            self._on_quit()
        self.stop()
    
    def _quick_dns(self, provider: str):
        """Cambio rápido de DNS."""
        # TODO: Implementar cambio de DNS
        print(f"Quick DNS change to: {provider}")
    
    def _quick_optimize(self, profile: str):
        """Aplicación rápida de perfil."""
        # TODO: Implementar optimización
        print(f"Quick optimize: {profile}")
    
    def _handle_quick_diagnostic(self):
        """Ejecuta diagnóstico rápido."""
        # TODO: Implementar diagnóstico
        print("Quick diagnostic")
    
    def _toggle_autostart(self):
        """Toggle iniciar con Windows."""
        # TODO: Implementar
        pass
    
    def _toggle_minimize_to_tray(self):
        """Toggle minimizar a tray."""
        # TODO: Implementar
        pass
    
    def _is_autostart_enabled(self) -> bool:
        """Verifica si autostart está habilitado."""
        # TODO: Implementar
        return False
    
    def _is_minimize_to_tray(self) -> bool:
        """Verifica si minimize to tray está habilitado."""
        return True
    
    def set_status(self, status: str, tooltip: Optional[str] = None):
        """
        Cambia el estado del icono.
        
        Args:
            status: "normal", "warning", "error", "disabled"
            tooltip: Texto del tooltip (opcional)
        """
        self._status = status
        if tooltip:
            self._tooltip = tooltip
        
        # Actualizar icono si está corriendo
        if self._icon:
            self._icon.icon = self._create_icon_image()
            self._icon.title = self._tooltip
    
    def show_notification(
        self,
        title: str,
        message: str,
        timeout: int = 5
    ):
        """Muestra una notificación desde el tray."""
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass
    
    def set_callbacks(
        self,
        on_show_window: Optional[Callable] = None,
        on_hide_window: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
    ):
        """Configura callbacks."""
        self._on_show_window = on_show_window
        self._on_hide_window = on_hide_window
        self._on_quit = on_quit
    
    def start(self):
        """Inicia el icono del tray en un thread separado."""
        if not PYSTRAY_AVAILABLE:
            print("pystray not available, skipping tray icon")
            return
        
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def _run(self):
        """Loop del tray icon."""
        try:
            self._icon = pystray.Icon(
                name="netboozt",
                icon=self._load_icon_image(),
                title=self._tooltip,
                menu=self._build_menu()
            )
            
            # Handler para doble click
            def on_activate(icon, item):
                if self.on_double_click:
                    self.on_double_click()
                elif self._on_show_window:
                    self._on_show_window()
            
            self._icon.run()
        except Exception as e:
            print(f"Tray icon error: {e}")
    
    def stop(self):
        """Detiene el icono del tray."""
        self._running = False
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
    
    def update_menu(self):
        """Actualiza el menú del tray."""
        if self._icon:
            self._icon.menu = self._build_menu()


# Singleton
_tray_instance: Optional[SystemTrayIcon] = None


def get_system_tray() -> SystemTrayIcon:
    """Obtiene instancia del tray icon."""
    global _tray_instance
    if _tray_instance is None:
        _tray_instance = SystemTrayIcon()
    return _tray_instance


def init_system_tray(
    on_show_window: Callable,
    on_quit: Callable,
    icon_path: Optional[Path] = None
) -> SystemTrayIcon:
    """
    Inicializa y retorna el tray icon configurado.
    """
    global _tray_instance
    _tray_instance = SystemTrayIcon(icon_path=icon_path)
    _tray_instance.set_callbacks(
        on_show_window=on_show_window,
        on_quit=on_quit
    )
    return _tray_instance


if __name__ == "__main__":
    # Test
    if not PYSTRAY_AVAILABLE:
        print("Install pystray: pip install pystray pillow")
        sys.exit(1)
    
    def show_window():
        print("Show window clicked!")
    
    def quit_app():
        print("Quit clicked!")
        tray.stop()
    
    tray = SystemTrayIcon()
    tray.set_callbacks(on_show_window=show_window, on_quit=quit_app)
    
    print("Starting tray icon... (check system tray)")
    print("Right-click the icon for menu, or double-click to show window")
    
    # En un programa real, esto correría en background
    tray._run()  # Blocking para test
