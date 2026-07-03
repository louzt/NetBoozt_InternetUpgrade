# NetBoozt Runner Strategy

**Proyecto**: `~/Proyectos/NetBoozt_InternetUpgrade/`
**Cargado en**: cualquier cwd bajo este proyecto

## Decisión de arquitectura

| Job | Runner | Pourquoi |
|---|---|---|
| Build Tauri Windows (`.exe`, NSIS) | **GitHub-hosted `windows-latest`** | El VPS es Linux, no puede compilar binarios Windows ni generar installers `.msi` via WiX |
| (future) Build Linux binario | **Self-hosted VPS** `hestiaweb@167.88.38.25:/opt/actions-runner` | Linux en Linux, sin costo de minutos |

## Regla dura

**Nunca cambiar `runs-on: windows-latest` a `runs-on: [self-hosted]` en workflows de este proyecto.** El self-hosted runner del VPS es Linux y no puede compilar Tauri para Windows.

## Hook companion

Antes de cualquier `gh workflow run` o `gh run list` que involucre `runs-on: [self-hosted]` en un workflow de este repo, verificar que el runner self-hosted sea capaz del target. Para Windows builds, **siempre GitHub-hosted**.

## Minutos GitHub Actions

- El build Windows quema ~7-8 min de GitHub Actions por release
- **No hay alternativa viable** dado que el app es Windows-only y el runner es Linux
- El self-hosted runner del VPS existe para otros proyectos (builds Linux, CI de crates Rust, etc.)
- Consulta `~/.claude/projects/-home-lou/memory/gh-self-hosted-runners-ref.md` para detalles del runner VPS

## Cuándo SÍ usar el runner del VPS

Proyectos donde:
- El target es Linux (`runs-on: ubuntu-latest` → `runs-on: [self-hosted, linux]`)
- El runner VPS tiene las herramientas necesarias (Rust, Node, etc.)
- No hay constraint de plataforma Windows

## Referencias

- Runner VPS: `/opt/actions-runner/` en `hestiaweb@167.88.38.25`
- Docs runner: `~/.claude/projects/-home-lou/memory/gh-self-hosted-runners-ref.md`
- Memory del runner en MEMORY.md: `gh-self-hosted-runners-ref`
