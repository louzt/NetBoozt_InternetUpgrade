#!/usr/bin/env python3
"""
NetBoozt Windows CLI Launcher
Ejecuta el CLI de la carpeta windows/

By LOUST (www.loust.pro)
"""

import sys
import subprocess
from pathlib import Path
import ctypes

# Directorio del script
REPO_ROOT = Path(__file__).parent
WINDOWS_DIR = REPO_ROOT / "windows"
CLI_SCRIPT = WINDOWS_DIR / "netboozt_cli.py"

def is_admin():
    """Verificar si tenemos permisos de admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    """Ejecutar CLI de Windows"""
    if not CLI_SCRIPT.exists():
        print(f"❌ Error: No se encuentra {CLI_SCRIPT}")
        print(f"   Asegúrate de estar en el directorio raíz del repo")
        sys.exit(1)
    
    # Mostrar modo admin si aplica
    if is_admin():
        print("⚡ Running with Administrator privileges\n")
    
    # Cambiar al directorio windows y ejecutar CLI
    try:
        # Pasar argumentos incluyendo 'asadmin' si viene
        subprocess.run(
            [sys.executable, str(CLI_SCRIPT)] + sys.argv[1:],
            cwd=str(WINDOWS_DIR),
            check=False
        )
    except KeyboardInterrupt:
        print("\n\nBye! 👋\n")
    except Exception as e:
        print(f"❌ Error ejecutando CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
