# NetBoozt - Releases Directory

Este directorio contiene los ejecutables compilados listos para distribución.

## 📁 Estructura

```
releases/
├── windows/                 # Ejecutables Windows
│   ├── NetBoozt_GUI.exe     # Interfaz gráfica con system tray
│   ├── NetBoozt_CLI.exe     # Línea de comandos
│   └── README.txt           # Instrucciones de uso
│
├── linux/                   # Futuro: AppImage o .deb
│   └── (coming soon)
│
└── macos/                   # Futuro: .app bundle
    └── (coming soon)
```

## 🚀 Cómo Compilar

### Windows (Python → Nuitka)

```powershell
# Desde la raíz del proyecto
.\scripts\build_nuitka.ps1

# Solo GUI
.\scripts\build_nuitka.ps1 -Target GUI

# Solo CLI
.\scripts\build_nuitka.ps1 -Target CLI
```

Los ejecutables se generan en `releases/windows/`.

### Windows (Rust/Tauri) - v3.0

```powershell
cd platforms/tauri
npm install
npm run tauri build
```

## 📦 Tamaños Esperados

| Ejecutable | Tecnología | Tamaño |
|------------|------------|--------|
| NetBoozt_GUI.exe | Python + Nuitka | ~25-35 MB |
| NetBoozt_CLI.exe | Python + Nuitka | ~20-25 MB |
| NetBoozt.exe | Rust + Tauri (v3.0) | ~5-10 MB |

## ⚡ Diferencias

| Característica | GUI | CLI |
|----------------|-----|-----|
| Ventana gráfica | ✅ | ❌ |
| System tray | ✅ | ❌ |
| Consola visible | ❌ | ✅ |
| Uso de RAM | ~80-120 MB | ~30-50 MB |
| Ideal para | Usuarios regulares | Servidores, scripts |

---

**Made by LOUST** (www.loust.pro)
