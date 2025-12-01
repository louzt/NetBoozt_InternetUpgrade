"""
NetBoozt - Build Verification System
Verifica que todo esté correcto antes de compilar

By LOUST (www.loust.pro)
"""

import sys
import os
from pathlib import Path
import importlib.util
import ast


class BuildVerifier:
    """Verificador de build"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.root = Path(__file__).parent
        
    def check_imports(self):
        """Verificar que todos los imports sean válidos"""
        print("🔍 Verificando imports...")
        
        src_path = self.root / "src"
        for py_file in src_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._verify_import(alias.name, py_file)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._verify_import(node.module, py_file)
            except SyntaxError as e:
                self.errors.append(f"❌ Syntax error en {py_file}: {e}")
            except Exception as e:
                self.warnings.append(f"⚠️ No se pudo parsear {py_file}: {e}")
    
    def _verify_import(self, module_name: str, file_path: Path):
        """Verificar que un import sea válido"""
        # Ignorar imports estándar y de terceros conocidos
        stdlib = {'os', 'sys', 'subprocess', 're', 'json', 'datetime', 'pathlib', 'typing', 'enum', 'dataclasses'}
        third_party = {'customtkinter', 'matplotlib', 'PIL', 'psutil', 'winotify', 'colorlog', 'tinydb', 'numpy', 'pandas'}
        
        base_module = module_name.split('.')[0]
        
        if base_module in stdlib or base_module in third_party:
            return
            
        # Verificar imports locales (src.*)
        if base_module == 'src' or base_module in ['gui', 'monitoring', 'optimizations', 'storage']:
            # OK - son imports locales
            return
    
    def check_required_files(self):
        """Verificar que existan todos los archivos necesarios"""
        print("📁 Verificando archivos requeridos...")
        
        required = [
            "src/__init__.py",
            "src/gui/__init__.py",
            "src/gui/modern_window.py",
            "src/gui/dashboard.py",
            "src/gui/about_tab.py",
            "src/monitoring/__init__.py",
            "src/monitoring/realtime_monitor.py",
            "src/monitoring/adapter_manager.py",
            "src/optimizations/__init__.py",
            "src/optimizations/detection.py",
            "src/storage/__init__.py",
            "src/storage/db_manager.py",
            "run_modern.py",
            "netboozt.spec",
            "requirements.txt",
            "assets/loust_logo.png",
            "assets/loust_icon.ico",
        ]
        
        for file_path in required:
            full_path = self.root / file_path
            if not full_path.exists():
                self.errors.append(f"❌ Archivo faltante: {file_path}")
    
    def check_dependencies(self):
        """Verificar que estén instaladas las dependencias"""
        print("📦 Verificando dependencias...")
        
        required_packages = {
            'customtkinter': '5.2.0',
            'matplotlib': '3.8.0',
            'tinydb': '4.8.0',
            'psutil': '5.9.0',
            'pyinstaller': '6.0.0',
        }
        
        for package, min_version in required_packages.items():
            try:
                # Intentar importar el paquete
                if package == 'pyinstaller':
                    # PyInstaller se instala como comando, verificar importando PyInstaller
                    import PyInstaller
                elif package == 'customtkinter':
                    import customtkinter
                elif package == 'matplotlib':
                    import matplotlib
                elif package == 'tinydb':
                    import tinydb
                elif package == 'psutil':
                    import psutil
            except ImportError:
                self.errors.append(f"❌ Paquete no instalado: {package}>={min_version}")
    
    def check_syntax_all_files(self):
        """Verificar sintaxis de todos los archivos Python"""
        print("✏️  Verificando sintaxis Python...")
        
        src_path = self.root / "src"
        for py_file in src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
            except SyntaxError as e:
                self.errors.append(f"❌ Error de sintaxis en {py_file.relative_to(self.root)}: línea {e.lineno}")
    
    def check_icon_files(self):
        """Verificar que los iconos existan y sean válidos"""
        print("🎨 Verificando iconos...")
        
        logo_path = self.root / "assets" / "loust_logo.png"
        icon_path = self.root / "assets" / "loust_icon.ico"
        
        if not logo_path.exists():
            self.errors.append(f"❌ Logo faltante: {logo_path}")
        elif logo_path.stat().st_size < 1000:
            self.warnings.append(f"⚠️ Logo muy pequeño: {logo_path.stat().st_size} bytes")
        
        if not icon_path.exists():
            self.errors.append(f"❌ Icono .ico faltante: {icon_path}")
        elif icon_path.stat().st_size < 1000:
            self.warnings.append(f"⚠️ Icono muy pequeño: {icon_path.stat().st_size} bytes")
    
    def run_all_checks(self):
        """Ejecutar todas las verificaciones"""
        print("=" * 60)
        print("🚀 NetBoozt - Verificación de Build")
        print("=" * 60)
        
        self.check_required_files()
        self.check_syntax_all_files()
        self.check_imports()
        self.check_dependencies()
        self.check_icon_files()
        
        print("\n" + "=" * 60)
        print("📊 RESULTADOS")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ ¡TODO CORRECTO! Listo para compilar.")
            return True
        elif not self.errors:
            print(f"\n✅ Sin errores críticos. {len(self.warnings)} advertencias.")
            return True
        else:
            print(f"\n❌ Build NO PUEDE continuar. Corrige los {len(self.errors)} errores primero.")
            return False


if __name__ == "__main__":
    verifier = BuildVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)
