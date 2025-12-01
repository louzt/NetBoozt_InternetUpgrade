# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file para NetBoozt
Genera un .exe con logo personalizado y tema oscuro
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os

# Paths
block_cipher = None
root_dir = os.path.abspath(SPECPATH)
assets_dir = os.path.join(root_dir, 'assets')

# Datos adicionales (assets, logo, etc.)
datas = []

# Logo de LOUST
logo_path = os.path.join(assets_dir, 'loust_logo.png')
icon_path = os.path.join(assets_dir, 'loust_icon.ico')

if os.path.exists(logo_path):
    datas.append((logo_path, 'assets'))

# CustomTkinter requiere sus assets
datas += collect_data_files('customtkinter')

# Incluir TODO el directorio src/ como data
src_dir = os.path.join(root_dir, 'src')
datas.append((src_dir, 'src'))

# Análisis de imports
a = Analysis(
    ['run_modern.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'psutil',
        'winotify',
        'colorlog',
        'tinydb',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.figure',
        'matplotlib.pyplot',
        'numpy',
    ] + collect_submodules('customtkinter') + collect_submodules('matplotlib') + collect_submodules('src'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtrar archivos innecesarios
a.binaries = [x for x in a.binaries if not x[0].startswith('_ssl')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NetBoozt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.exists(icon_path) else None,  # Logo de LOUST
    version='version_info.txt',  # Información de versión con LOUST como autor
    uac_admin=True,  # Solicitar permisos de admin automáticamente
)

# Opcional: Crear installer con NSIS
# coll = COLLECT(...)
