"""
NetBoozt - Launcher Moderno con Splash Screen
Ejecuta la interfaz moderna con CustomTkinter
"""

import sys
import os
from pathlib import Path
import psutil
import time

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Iniciar logging PRIMERO
from utils.logger import log_info, log_error, log_critical, log_warning, LogSection

log_info("="*80)
log_info("NetBoozt Application Starting")
log_info("="*80)

# Limpiar instancias previas de NetBoozt
def cleanup_previous_instances():
    """Matar instancias previas de NetBoozt.exe"""
    current_pid = os.getpid()
    killed = 0
    
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Verificar nombre de proceso de forma segura
                if proc.info and proc.info.get('name') == 'NetBoozt.exe' and proc.info['pid'] != current_pid:
                    try:
                        proc.kill()
                        killed += 1
                        log_warning(f"Killed previous instance (PID: {proc.info['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                # Proceso puede haber terminado o no tener permisos
                continue
        
        if killed > 0:
            log_info(f"Cleaned up {killed} previous instance(s)")
            time.sleep(0.5)  # Esperar a que se liberen recursos
    except Exception as e:
        log_error("Error during cleanup", e)

# Limpiar antes de iniciar
cleanup_previous_instances()

# Ocultar consola en Windows al ejecutar como .exe
if getattr(sys, 'frozen', False):
    try:
        import ctypes
        # Ocultar ventana de consola
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        log_info("Console window hidden (frozen mode)")
    except Exception as e:
        log_error("Failed to hide console", e)

if __name__ == "__main__":
    try:
        with LogSection("Splash Screen Initialization"):
            from src.gui.splash_screen import SplashScreen
            from src.gui.modern_window import ModernNetBoozt
            from src.gui.error_dialog import show_error_dialog
            import customtkinter as ctk
            
            log_info("Importing modules completed")
            
            # Crear ventana raíz oculta para splash
            root = ctk.CTk()
            root.withdraw()
            log_info("Root window created (hidden)")
            
            # Mostrar splash
            splash = SplashScreen(root)
            log_info("Splash screen created")
            
            # Actualizar splash con progreso simulado
            splash.update_status("Cargando módulos...", 0.3)
            splash.update()
            
            splash.update_status("Inicializando interfaz...", 0.6)
            splash.update()
            
            splash.update_status("✓ Listo", 1.0)
            splash.update()
            
            # Función para cerrar splash y mostrar app
            def show_main_app():
                try:
                    # Destruir splash y root
                    splash.destroy()
                    root.destroy()
                    log_info("Splash closed")
                    
                    # IMPORTANTE: Crear app en main thread DESPUÉS de cerrar splash
                    with LogSection("Application Initialization"):
                        log_info("Creating ModernNetBoozt instance in main thread...")
                        app = ModernNetBoozt()
                        log_info("ModernNetBoozt instance created successfully")
                        
                        # Mostrar ventana principal
                        app.deiconify()
                        log_info("Main window shown")
                        
                        # Ejecutar mainloop
                        log_info("Running main application loop...")
                        app.mainloop()
                        log_info("Application closed normally")
                        
                except Exception as e:
                    log_critical("Failed to initialize application", e)
                    
                    # Mostrar error
                    error_details = f"{type(e).__name__}: {str(e)}"
                    log_error(f"Error details: {error_details}")
                    
                    try:
                        temp_root = ctk.CTk()
                        temp_root.withdraw()
                        show_error_dialog(
                            temp_root,
                            "Error al inicializar NetBoozt",
                            "No se pudo cargar la aplicación correctamente.\n\n" +
                            "Por favor revisa los logs o reporta este error.",
                            error_details
                        )
                        temp_root.destroy()
                    except:
                        pass
                    
                    sys.exit(1)
            
            # Programar cierre de splash y apertura de app principal
            splash.after(800, show_main_app)
            
            # Ejecutar splash mainloop (bloquea hasta que se cierre)
            log_info("Running splash mainloop...")
            splash.mainloop()
            
    except Exception as e:
        log_critical("Fatal error in main", e)
        import traceback
        traceback.print_exc()
        
        # Intentar mostrar diálogo de error
        try:
            import customtkinter as ctk
            from src.gui.error_dialog import show_error_dialog
            root = ctk.CTk()
            root.withdraw()
            
            show_error_dialog(
                root,
                "Error Fatal",
                "Ocurrió un error crítico al iniciar NetBoozt.\n\n" +
                "Por favor revisa los logs o contacta soporte.",
                f"{type(e).__name__}: {str(e)}"
            )
            root.destroy()
        except:
            pass
        
        sys.exit(1)
