# 🏗️ NetBoozt - Decisión de Lenguaje y Arquitectura Multi-Plataforma

> **Documento de Arquitectura** | NetBoozt v2.2+  
> **Por LOUST** (www.loust.pro)  
> **Última actualización:** Diciembre 2025

---

## 📋 Resumen Ejecutivo

Este documento analiza las opciones de lenguajes de programación para el frontend de NetBoozt, comparando el actual (Python/CustomTkinter) con alternativas de mayor rendimiento, y establece una estrategia de migración en dos fases.

| Fase | Tecnología | Timeline | Beneficio Principal |
|------|------------|----------|---------------------|
| **Fase 1** | Nuitka (Python compilado) | 1-2 semanas | Mejora inmediata sin reescribir |
| **Fase 2** | Rust + Tauri | 4-6 meses | App nativa premium |

---

## 🎯 Contexto del Proyecto

### Stack Actual (v2.x)

| Componente | Tecnología | Notas |
|------------|------------|-------|
| **Lenguaje** | Python 3.11+ | Interpretado |
| **GUI Framework** | CustomTkinter | Basado en Tk/Tcl |
| **Empaquetado** | PyInstaller | Genera .exe grande |
| **APIs Windows** | subprocess → PowerShell | Comandos de red |
| **Gráficas** | matplotlib | Consumo de memoria alto |
| **Base de datos** | TinyDB | JSON ligero |

### Métricas Actuales (PyInstaller)

| Métrica | Valor | Problema |
|---------|-------|----------|
| Tamaño .exe | 80-120 MB | Muy grande |
| Tiempo inicio | 3-5 segundos | Lento |
| RAM en reposo | 150-200 MB | Alto para una utilidad |
| CPU (monitoreo) | 5-10% | Aceptable |

---

## 📊 Análisis Comparativo de Alternativas

### Tabla de Comparación

| Criterio | **Rust + Tauri** | **Rust + egui** | **C++ + Qt** | **Go + Fyne** | **Nuitka** | **Cython** |
|----------|------------------|-----------------|--------------|---------------|------------|------------|
| **Rendimiento (CPU)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Uso de Memoria** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Tiempo de Inicio** | 0.3-0.8s | 0.1-0.2s | 0.2-0.5s | 0.3-0.5s | 1-2s | 2-4s |
| **Tamaño .exe** | 3-10 MB | 2-5 MB | 15-40 MB | 8-15 MB | 15-30 MB | 50-150 MB |
| **Facilidad Migración** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **APIs Windows** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Curva Aprendizaje** | Media-Alta | Alta | Alta | Media | Baja | Baja |
| **Look Profesional** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🦀 Opción 1: Rust + Tauri (Recomendado para v3.0)

### ¿Por qué Tauri?

Tauri combina lo mejor de dos mundos:
- **Frontend Web** (HTML/CSS/JS) → Flexibilidad y UI moderna
- **Backend Rust** → Rendimiento nativo y seguridad de memoria

### Arquitectura Propuesta

```
platforms/tauri/
├── src-tauri/                # Backend Rust
│   ├── Cargo.toml
│   └── src/
│       ├── main.rs           # Entry point
│       ├── lib.rs            # Exports
│       ├── commands/         # Tauri commands
│       │   ├── mod.rs
│       │   ├── network.rs    # Get-NetAdapter, etc.
│       │   ├── dns.rs        # DNS operations
│       │   ├── optimizer.rs  # TCP optimizations
│       │   └── diagnostics.rs
│       ├── monitor/          # Background monitoring
│       │   ├── mod.rs
│       │   ├── realtime.rs
│       │   └── events.rs
│       └── windows/          # Windows API wrappers
│           ├── mod.rs
│           ├── powershell.rs
│           ├── wmi.rs
│           └── event_log.rs
├── src/                      # Frontend Web
│   ├── lib/
│   │   ├── components/
│   │   │   ├── Dashboard.svelte
│   │   │   ├── Optimizations.svelte
│   │   │   ├── DNSFailover.svelte
│   │   │   ├── Diagnostics.svelte
│   │   │   └── Settings.svelte
│   │   ├── stores/
│   │   │   ├── network.ts
│   │   │   └── settings.ts
│   │   └── utils/
│   │       └── api.ts
│   ├── app.html
│   ├── app.css
│   └── routes/
│       └── +page.svelte
├── static/
│   └── assets/
└── package.json
```

### Ejemplo: Comando PowerShell en Tauri

```rust
// src-tauri/src/commands/network.rs
use std::process::Command;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct NetworkAdapter {
    pub name: String,
    pub status: String,
    pub link_speed: String,
    pub mac_address: String,
}

#[tauri::command]
pub async fn get_network_adapters() -> Result<Vec<NetworkAdapter>, String> {
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            "Get-NetAdapter | Where-Object Status -eq 'Up' | \
             Select-Object Name, Status, LinkSpeed, MacAddress | \
             ConvertTo-Json"
        ])
        .output()
        .map_err(|e| e.to_string())?;
    
    let json = String::from_utf8_lossy(&output.stdout);
    let adapters: Vec<NetworkAdapter> = serde_json::from_str(&json)
        .map_err(|e| e.to_string())?;
    
    Ok(adapters)
}

#[tauri::command]
pub async fn set_dns_servers(
    adapter: String, 
    primary: String, 
    secondary: Option<String>
) -> Result<bool, String> {
    let dns_list = match secondary {
        Some(sec) => format!("{},{}", primary, sec),
        None => primary.clone(),
    };
    
    let output = Command::new("powershell")
        .args([
            "-NoProfile",
            "-Command",
            &format!(
                "Set-DnsClientServerAddress -InterfaceAlias '{}' -ServerAddresses {}",
                adapter, dns_list
            )
        ])
        .output()
        .map_err(|e| e.to_string())?;
    
    Ok(output.status.success())
}
```

### Ejemplo: Frontend Svelte

```svelte
<!-- src/lib/components/Dashboard.svelte -->
<script lang="ts">
  import { invoke } from '@tauri-apps/api/tauri';
  import { onMount } from 'svelte';
  
  interface NetworkAdapter {
    name: string;
    status: string;
    link_speed: string;
    mac_address: string;
  }
  
  let adapters: NetworkAdapter[] = [];
  let loading = true;
  
  onMount(async () => {
    adapters = await invoke('get_network_adapters');
    loading = false;
  });
  
  async function setCloudflare(adapter: string) {
    const success = await invoke('set_dns_servers', {
      adapter,
      primary: '1.1.1.1',
      secondary: '1.0.0.1'
    });
    if (success) {
      // Show toast notification
    }
  }
</script>

<div class="dashboard">
  <h2>Network Adapters</h2>
  
  {#if loading}
    <div class="spinner" />
  {:else}
    {#each adapters as adapter}
      <div class="adapter-card">
        <h3>{adapter.name}</h3>
        <p>Status: {adapter.status}</p>
        <p>Speed: {adapter.link_speed}</p>
        <button on:click={() => setCloudflare(adapter.name)}>
          Use Cloudflare DNS
        </button>
      </div>
    {/each}
  {/if}
</div>

<style>
  .dashboard {
    padding: 1rem;
  }
  .adapter-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem 0;
  }
</style>
```

### Ventajas de Tauri para NetBoozt

| Aspecto | Beneficio |
|---------|-----------|
| **UI Moderna** | SvelteKit/React + CSS = diseño premium |
| **Tamaño** | 5-10 MB vs 80-120 MB actual |
| **Inicio** | 0.3-0.5s vs 3-5s actual |
| **Memoria** | 40-60 MB vs 150-200 MB actual |
| **Seguridad** | Rust = memory safety |
| **Ecosistema** | npm + cargo = librerías infinitas |

### Desventajas

| Aspecto | Desventaja | Mitigación |
|---------|------------|------------|
| **Reescritura** | 100% código nuevo | Migración gradual |
| **Curva** | Aprender Rust | Copilot/AI asiste |
| **WebView** | Depende de Edge WebView2 | Viene con Windows 11 |
| **Tiempo** | 4-6 meses desarrollo | Fase 1 con Nuitka mientras |

---

## 🐍 Opción 2: Nuitka (Recomendado para v2.x inmediato)

### ¿Por qué Nuitka Primero?

Nuitka compila Python a C y luego a código máquina nativo:

```
Python (.py) → C código → Compilador C → Binario nativo (.exe)
```

**Beneficio clave: CERO cambios de código.**

### Comando de Compilación para NetBoozt

```powershell
# Instalar Nuitka
pip install nuitka ordered-set zstandard

# Compilar NetBoozt
python -m nuitka `
    --standalone `
    --onefile `
    --enable-plugin=tk-inter `
    --include-data-dir=assets=assets `
    --windows-icon-from-ico=assets/icon.ico `
    --windows-console-mode=disable `
    --windows-company-name="LOUST" `
    --windows-product-name="NetBoozt" `
    --windows-file-version=2.2.0.0 `
    --windows-product-version=2.2.0.0 `
    --windows-file-description="Network Optimization Tool" `
    --output-dir=dist `
    --output-filename=NetBoozt.exe `
    run_modern.py
```

### Mejoras Esperadas con Nuitka

| Métrica | PyInstaller | Nuitka | Mejora |
|---------|-------------|--------|--------|
| **Tamaño .exe** | 80-120 MB | 25-35 MB | **-60%** |
| **Tiempo inicio** | 3-5 seg | 1-2 seg | **-50%** |
| **RAM reposo** | 150-200 MB | 80-120 MB | **-40%** |
| **Velocidad código** | 1x | 2-4x | **+200%** |

### Configuración Nuitka (`nuitka.json`)

```json
{
  "main": "run_modern.py",
  "standalone": true,
  "onefile": true,
  "output-dir": "dist",
  "output-filename": "NetBoozt.exe",
  "enable-plugins": ["tk-inter"],
  "include-data-dirs": ["assets=assets"],
  "windows-icon-from-ico": "assets/icon.ico",
  "windows-console-mode": "disable",
  "windows-company-name": "LOUST",
  "windows-product-name": "NetBoozt",
  "windows-file-version": "2.2.0.0",
  "windows-product-version": "2.2.0.0"
}
```

---

## ⚖️ Comparación de Otras Opciones

### C++ + Qt

**Ventajas:**
- Framework más maduro (25+ años)
- Qt Quick/QML = UIs fluidas
- Usado en OBS, VirtualBox, etc.

**Desventajas:**
- Licenciamiento complejo (LGPL o comercial $$)
- Ejecutables grandes (15-40 MB)
- Curva de aprendizaje alta

**Veredicto:** Overkill para NetBoozt, mejor para proyectos enterprise.

### Go + Fyne

**Ventajas:**
- Compilación simple a binario único
- Sintaxis más fácil que Rust
- Buena concurrencia (goroutines)

**Desventajas:**
- Look de Fyne menos pulido
- Ecosistema Windows limitado
- Gráficas limitadas

**Veredicto:** Bueno para CLIs, no ideal para GUI rica.

### Rust + egui/iced

**Ventajas:**
- GUI 100% nativa (sin WebView)
- Máximo rendimiento
- Immediate mode = código simple

**Desventajas:**
- Look menos "web-moderno"
- Ecosistema de componentes pequeño
- Gráficas complejas difíciles

**Veredicto:** Bueno para herramientas de desarrollo, no para apps consumer.

### Cython + PyInstaller

**Ventajas:**
- Optimiza hotspots sin reescribir todo
- Compatible con código existente

**Desventajas:**
- Mejora limitada para código I/O-bound
- Ejecutables siguen siendo grandes
- Complejidad añadida

**Veredicto:** Mejor usar Nuitka que ofrece más por menos esfuerzo.

---

## 🗺️ Roadmap de Migración

### Fase 1: Nuitka (v2.2 - v2.x) — Inmediato

```
Timeline: 1-2 semanas
Esfuerzo: Bajo
Riesgo: Mínimo

Tareas:
[x] Instalar Nuitka y dependencias
[ ] Configurar build script con Nuitka
[ ] Testing del ejecutable compilado
[ ] Comparar métricas (tamaño, inicio, RAM)
[ ] Documentar proceso de build
```

### Fase 2: Tauri (v3.0) — Largo Plazo

```
Timeline: 4-6 meses
Esfuerzo: Alto
Riesgo: Medio (mitigado por Fase 1)

Tareas:
[ ] Setup proyecto Tauri + SvelteKit
[ ] Migrar backend: comandos PowerShell → Rust
[ ] Migrar frontend: CustomTkinter → Svelte
[ ] Reimplementar monitoreo en tiempo real
[ ] Testing exhaustivo en Windows 10/11
[ ] Beta testing con usuarios
[ ] Release v3.0
```

### Diagrama de Migración

```
v2.1 (PyInstaller)
    │
    ▼
v2.2 (Nuitka) ──────────────────┐
    │                           │
    │ ← Mejoras inmediatas      │
    │   sin reescribir          │
    ▼                           │
v2.3-2.x (Nuitka + mejoras)     │
    │                           │
    │                           ▼
    │              Desarrollo paralelo
    │              de Tauri v3.0
    │                           │
    ▼                           ▼
v3.0 (Tauri) ←──────────────────┘
```

---

## 📂 Nueva Estructura del Proyecto

```
NetBoozt/
├── platforms/                    # Código específico por plataforma/lenguaje
│   ├── python/                   # Versión Python actual (v2.x)
│   │   ├── src/                  # Código fuente Python
│   │   ├── assets/               # Assets de la app
│   │   ├── tests/                # Tests Python
│   │   ├── requirements.txt
│   │   ├── run_modern.py         # Entry point GUI
│   │   ├── netboozt_cli.py       # CLI
│   │   └── netboozt.spec         # PyInstaller spec
│   │
│   ├── tauri/                    # Versión Tauri (v3.0 - futuro)
│   │   ├── src-tauri/            # Backend Rust
│   │   ├── src/                  # Frontend Web (Svelte)
│   │   └── package.json
│   │
│   └── linux/                    # Versión Linux (futuro)
│       └── ...
│
├── shared/                       # Código/config compartido entre plataformas
│   ├── dns_servers.json          # Lista de DNS servers
│   ├── optimizations.json        # Definiciones de optimizaciones
│   └── translations/             # Traducciones i18n
│       ├── en.json
│       └── es.json
│
├── scripts/                      # Scripts de build/desarrollo
│   ├── build_python.ps1          # Build con PyInstaller
│   ├── build_nuitka.ps1          # Build con Nuitka
│   ├── build_tauri.ps1           # Build Tauri (futuro)
│   └── dev.ps1                   # Modo desarrollo
│
├── docs/                         # Documentación
│   ├── architecture/             # Docs de arquitectura
│   │   ├── LANGUAGE_DECISION.md  # Este documento
│   │   └── ...
│   ├── optimizations/            # Docs técnicos
│   └── es/                       # Docs en español
│
├── tools/                        # Herramientas de desarrollo
├── logs/                         # Logs de la aplicación
│
├── README.md
├── README.es.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── pyproject.toml
```

---

## 🔑 Decisión Final

### Para NetBoozt, recomendamos:

| Corto Plazo (v2.2-2.x) | Largo Plazo (v3.0+) |
|------------------------|---------------------|
| **Nuitka** | **Rust + Tauri** |
| Mejora inmediata | App premium nativa |
| Sin reescribir código | UI web moderna |
| 1-2 semanas | 4-6 meses |

### Justificación

1. **Nuitka ahora** = resultados inmediatos con riesgo cero
2. **Tauri después** = visión a largo plazo para producto premium
3. **No elegir solo uno** = estrategia de migración gradual
4. **Usuarios contentos** = app mejorada mientras se desarrolla v3.0

---

## 📚 Referencias

- [Tauri Documentation](https://tauri.app/v1/guides/)
- [Nuitka User Manual](https://nuitka.net/doc/user-manual.html)
- [Rust Book](https://doc.rust-lang.org/book/)
- [SvelteKit Docs](https://kit.svelte.dev/docs)
- [windows-rs crate](https://github.com/microsoft/windows-rs)

---

<div align="center">

**Made with ❤️ by [LOUST](https://www.loust.pro)**

</div>
