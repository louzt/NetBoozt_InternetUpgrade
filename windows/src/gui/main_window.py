"""
GUI Moderna para Windows Network Optimizer
Interfaz gráfica con diseño moderno usando tkinter + ttkbootstrap

By LOUST (www.loust.pro)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ttkbootstrap as ttk_boot
    from ttkbootstrap.constants import *
    MODERN_THEME = True
except ImportError:
    MODERN_THEME = False
    print("⚠️  ttkbootstrap no instalado. Usando tkinter estándar")
    print("   Instalar con: pip install ttkbootstrap")

from optimizations.network_optimizer import WindowsNetworkOptimizer, OptimizationLevel


class NetworkOptimizerGUI:
    """Interfaz gráfica moderna para el optimizador de red"""
    
    def __init__(self):
        # Crear ventana principal
        if MODERN_THEME:
            self.root = ttk_boot.Window(themename="darkly")
        else:
            self.root = tk.Tk()
        
        self.root.title("Windows Network Optimizer - By LOUST")
        self.root.geometry("1000x700")
        
        # Optimizer instance
        self.optimizer = WindowsNetworkOptimizer()
        
        # Variables
        self.selected_optimizations = {}
        
        # Construir UI
        self.build_ui()
        
        # Cargar estado actual
        self.load_current_state()
    
    def build_ui(self):
        """Construir interfaz de usuario"""
        
        # === HEADER ===
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = ttk.Label(
            header_frame,
            text="🚀 Windows Network Optimizer",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(
            header_frame,
            text="By LOUST (www.loust.pro)",
            font=("Segoe UI", 10)
        )
        subtitle_label.pack(side=tk.LEFT, padx=20)
        
        # === TABS ===
        if MODERN_THEME:
            notebook = ttk_boot.Notebook(self.root, bootstyle="dark")
        else:
            notebook = ttk.Notebook(self.root)
        
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tab 1: Optimizaciones
        opt_tab = ttk.Frame(notebook)
        notebook.add(opt_tab, text="🔧 Optimizaciones")
        self.build_optimizations_tab(opt_tab)
        
        # Tab 2: Perfiles
        profiles_tab = ttk.Frame(notebook)
        notebook.add(profiles_tab, text="📊 Perfiles")
        self.build_profiles_tab(profiles_tab)
        
        # Tab 3: Estado Actual
        status_tab = ttk.Frame(notebook)
        notebook.add(status_tab, text="📈 Estado Actual")
        self.build_status_tab(status_tab)
        
        # Tab 4: Acerca de
        about_tab = ttk.Frame(notebook)
        notebook.add(about_tab, text="ℹ️ Acerca de")
        self.build_about_tab(about_tab)
        
        # === FOOTER ===
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = ttk.Label(
            footer_frame,
            text="✅ Listo para optimizar",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Botón de aplicar
        if MODERN_THEME:
            apply_btn = ttk_boot.Button(
                footer_frame,
                text="Aplicar Seleccionadas",
                bootstyle="success",
                command=self.apply_selected
            )
        else:
            apply_btn = ttk.Button(
                footer_frame,
                text="Aplicar Seleccionadas",
                command=self.apply_selected
            )
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        # Botón de reset
        if MODERN_THEME:
            reset_btn = ttk_boot.Button(
                footer_frame,
                text="Restaurar Defaults",
                bootstyle="danger",
                command=self.reset_defaults
            )
        else:
            reset_btn = ttk.Button(
                footer_frame,
                text="Restaurar Defaults",
                command=self.reset_defaults
            )
        reset_btn.pack(side=tk.RIGHT, padx=5)
    
    def build_optimizations_tab(self, parent):
        """Construir tab de optimizaciones individuales"""
        
        # Frame con scroll
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Agrupar por categoría
        categories = {}
        for opt_id, opt in self.optimizer.optimizations.items():
            if opt.category not in categories:
                categories[opt.category] = []
            categories[opt.category].append((opt_id, opt))
        
        # Crear UI para cada categoría
        for category, opts in categories.items():
            # Frame de categoría
            cat_frame = ttk.LabelFrame(scrollable_frame, text=category, padding=10)
            cat_frame.pack(fill=tk.X, padx=10, pady=5)
            
            for opt_id, opt in opts:
                # Frame de optimización
                opt_frame = ttk.Frame(cat_frame)
                opt_frame.pack(fill=tk.X, pady=5)
                
                # Checkbox
                var = tk.BooleanVar(value=False)
                self.selected_optimizations[opt_id] = var
                
                check = ttk.Checkbutton(
                    opt_frame,
                    text=opt.name,
                    variable=var
                )
                check.pack(side=tk.LEFT)
                
                # Badge de riesgo
                risk_colors = {
                    "low": "green",
                    "medium": "orange",
                    "high": "red"
                }
                
                risk_label = ttk.Label(
                    opt_frame,
                    text=f"[{opt.risk_level.upper()}]",
                    foreground=risk_colors.get(opt.risk_level, "gray")
                )
                risk_label.pack(side=tk.LEFT, padx=10)
                
                # Descripción
                desc_label = ttk.Label(
                    opt_frame,
                    text=opt.description,
                    wraplength=700,
                    justify=tk.LEFT
                )
                desc_label.pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def build_profiles_tab(self, parent):
        """Construir tab de perfiles predefinidos"""
        
        info_frame = ttk.Frame(parent, padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            info_frame,
            text="Perfiles de Optimización",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            info_frame,
            text="Selecciona un perfil predefinido según tu uso:",
            font=("Segoe UI", 10)
        ).pack(pady=5)
        
        # Conservative
        cons_frame = ttk.LabelFrame(info_frame, text="🟢 Conservative", padding=15)
        cons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            cons_frame,
            text="Solo optimizaciones probadas y seguras (risk: low).\n"
                 "Ideal para usuarios que buscan mejoras sin riesgos.",
            wraplength=800,
            justify=tk.LEFT
        ).pack(side=tk.LEFT)
        
        if MODERN_THEME:
            ttk_boot.Button(
                cons_frame,
                text="Aplicar",
                bootstyle="success-outline",
                command=lambda: self.apply_profile(OptimizationLevel.CONSERVATIVE)
            ).pack(side=tk.RIGHT)
        else:
            ttk.Button(
                cons_frame,
                text="Aplicar",
                command=lambda: self.apply_profile(OptimizationLevel.CONSERVATIVE)
            ).pack(side=tk.RIGHT)
        
        # Balanced
        bal_frame = ttk.LabelFrame(info_frame, text="🟡 Balanced", padding=15)
        bal_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            bal_frame,
            text="Balance entre rendimiento y estabilidad (risk: low + medium).\n"
                 "Recomendado para la mayoría de usuarios.",
            wraplength=800,
            justify=tk.LEFT
        ).pack(side=tk.LEFT)
        
        if MODERN_THEME:
            ttk_boot.Button(
                bal_frame,
                text="Aplicar",
                bootstyle="warning-outline",
                command=lambda: self.apply_profile(OptimizationLevel.BALANCED)
            ).pack(side=tk.RIGHT)
        else:
            ttk.Button(
                bal_frame,
                text="Aplicar",
                command=lambda: self.apply_profile(OptimizationLevel.BALANCED)
            ).pack(side=tk.RIGHT)
        
        # Aggressive
        agg_frame = ttk.LabelFrame(info_frame, text="🔴 Aggressive", padding=15)
        agg_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(
            agg_frame,
            text="Todas las optimizaciones (risk: all).\n"
                 "Solo para usuarios avanzados. Máximo rendimiento.",
            wraplength=800,
            justify=tk.LEFT
        ).pack(side=tk.LEFT)
        
        if MODERN_THEME:
            ttk_boot.Button(
                agg_frame,
                text="Aplicar",
                bootstyle="danger-outline",
                command=lambda: self.apply_profile(OptimizationLevel.AGGRESSIVE)
            ).pack(side=tk.RIGHT)
        else:
            ttk.Button(
                agg_frame,
                text="Aplicar",
                command=lambda: self.apply_profile(OptimizationLevel.AGGRESSIVE)
            ).pack(side=tk.RIGHT)
    
    def build_status_tab(self, parent):
        """Construir tab de estado actual"""
        
        status_frame = ttk.Frame(parent, padding=20)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            status_frame,
            text="Estado Actual del Sistema",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=10)
        
        # Text widget con scroll para mostrar configuración
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            width=100,
            height=30,
            font=("Consolas", 9)
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Botón de refresh
        if MODERN_THEME:
            ttk_boot.Button(
                status_frame,
                text="🔄 Actualizar Estado",
                bootstyle="info",
                command=self.refresh_status
            ).pack()
        else:
            ttk.Button(
                status_frame,
                text="🔄 Actualizar Estado",
                command=self.refresh_status
            ).pack()
    
    def build_about_tab(self, parent):
        """Construir tab de información"""
        
        about_frame = ttk.Frame(parent, padding=40)
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            about_frame,
            text="Windows Network Optimizer",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            about_frame,
            text="Versión 1.0.0",
            font=("Segoe UI", 12)
        ).pack()
        
        ttk.Label(
            about_frame,
            text="\nBy LOUST",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            about_frame,
            text="www.loust.pro",
            font=("Segoe UI", 12),
            foreground="blue",
            cursor="hand2"
        ).pack()
        
        ttk.Label(
            about_frame,
            text="\n" + "="*50 + "\n\n"
                 "Optimizaciones TCP/IP equivalentes a BBR de Linux\n"
                 "para Windows 10/11.\n\n"
                 "Incluye:\n"
                 "• TCP Congestion Control (NewReno)\n"
                 "• Receive Side Scaling (RSS)\n"
                 "• HyStart++ Algorithm\n"
                 "• Proportional Rate Reduction (PRR)\n"
                 "• ECN (Explicit Congestion Notification)\n"
                 "• TCP Fast Open\n"
                 "• Pacing Optimizations\n"
                 "• Y más...\n\n"
                 "Todas las optimizaciones han sido probadas en\n"
                 "entornos de producción y son seguras para uso general.\n\n"
                 "=" * 50,
            font=("Segoe UI", 10),
            justify=tk.CENTER
        ).pack(pady=20)
        
        ttk.Label(
            about_frame,
            text="⚠️ Requiere permisos de administrador",
            font=("Segoe UI", 10, "bold"),
            foreground="orange"
        ).pack(pady=10)
    
    def load_current_state(self):
        """Cargar estado actual del sistema"""
        # TODO: Implementar lectura de configuración actual
        pass
    
    def refresh_status(self):
        """Actualizar estado del sistema"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, "Obteniendo configuración actual...\n\n")
        
        # Ejecutar en thread separado
        def get_status():
            report = self.optimizer.generate_report()
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, report)
        
        thread = threading.Thread(target=get_status)
        thread.start()
    
    def apply_selected(self):
        """Aplicar optimizaciones seleccionadas"""
        selected = [opt_id for opt_id, var in self.selected_optimizations.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Advertencia", "No has seleccionado ninguna optimización")
            return
        
        # Confirmar
        if not messagebox.askyesno(
            "Confirmar",
            f"¿Aplicar {len(selected)} optimizaciones?\n\n"
            "Requiere permisos de administrador."
        ):
            return
        
        # Aplicar en thread separado
        def apply():
            self.status_label.config(text="⏳ Aplicando optimizaciones...")
            
            success_count = 0
            for opt_id in selected:
                if self.optimizer.apply_optimization(opt_id):
                    success_count += 1
            
            self.status_label.config(
                text=f"✅ Aplicadas {success_count}/{len(selected)} optimizaciones"
            )
            
            messagebox.showinfo(
                "Completado",
                f"Optimizaciones aplicadas: {success_count}/{len(selected)}\n\n"
                "Puede ser necesario reiniciar para ver todos los cambios."
            )
        
        thread = threading.Thread(target=apply)
        thread.start()
    
    def apply_profile(self, level: OptimizationLevel):
        """Aplicar perfil predefinido"""
        level_names = {
            OptimizationLevel.CONSERVATIVE: "Conservative (Seguro)",
            OptimizationLevel.BALANCED: "Balanced (Recomendado)",
            OptimizationLevel.AGGRESSIVE: "Aggressive (Avanzado)"
        }
        
        if not messagebox.askyesno(
            "Confirmar Perfil",
            f"¿Aplicar perfil {level_names[level]}?\n\n"
            "Requiere permisos de administrador."
        ):
            return
        
        # Aplicar en thread separado
        def apply():
            self.status_label.config(text=f"⏳ Aplicando perfil {level.value}...")
            results = self.optimizer.apply_profile(level)
            
            success = sum(1 for v in results.values() if v)
            total = len(results)
            
            self.status_label.config(
                text=f"✅ Perfil aplicado: {success}/{total} optimizaciones"
            )
            
            messagebox.showinfo(
                "Completado",
                f"Perfil {level_names[level]} aplicado.\n\n"
                f"Exitosas: {success}/{total}\n\n"
                "Puede ser necesario reiniciar."
            )
        
        thread = threading.Thread(target=apply)
        thread.start()
    
    def reset_defaults(self):
        """Restaurar configuración por defecto"""
        if not messagebox.askyesno(
            "Confirmar Reset",
            "¿Restaurar configuración TCP/IP a valores por defecto de Windows?\n\n"
            "Esto revertirá TODAS las optimizaciones.\n"
            "Requiere reinicio del sistema."
        ):
            return
        
        if self.optimizer.reset_to_defaults():
            messagebox.showinfo(
                "Completado",
                "Configuración restaurada a valores por defecto.\n\n"
                "Reinicia el sistema para aplicar los cambios."
            )
        else:
            messagebox.showerror(
                "Error",
                "Error restaurando configuración.\n"
                "Verifica permisos de administrador."
            )
    
    def run(self):
        """Iniciar GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = NetworkOptimizerGUI()
    app.run()
