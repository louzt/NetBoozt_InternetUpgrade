"""
Windows Network Optimizer
Launcher principal
"""

import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gui.main_window import NetworkOptimizerGUI

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Windows Network Optimizer                            ║
║         By LOUST (www.loust.pro)                             ║
╚══════════════════════════════════════════════════════════════╝

⚠️  IMPORTANTE: Ejecuta este script como ADMINISTRADOR

Iniciando GUI...
    """)
    
    app = NetworkOptimizerGUI()
    app.run()
