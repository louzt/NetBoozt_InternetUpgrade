# Changelog

Todos los cambios notables en NetBoozt serán documentados aquí.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2024-01-20

### 🎉 Lanzamiento Inicial

#### ✨ Agregado
- **Windows Module**: Sistema completo de optimización TCP/IP
  - 15+ optimizaciones implementadas (RSS, ECN, HyStart, PRR, etc.)
  - GUI moderna con ttkbootstrap (tema Darkly)
  - 3 perfiles: Conservative, Balanced, Aggressive
  - Sistema de backup/restore automático
  - Verificación de permisos admin
  
- **Optimizaciones Implementadas**:
  - TCP Window Scaling (RFC 7323)
  - Receive Side Scaling (RSS)
  - Explicit Congestion Notification (ECN)
  - HyStart++ (Slow Start mejora)
  - Proportional Rate Reduction (PRR)
  - TCP Fast Open (TFO)
  - Pacing mejorado
  - NewReno congestion control
  - Initial RTO optimization
  - Receive Window Auto-Tuning
  - Network Throttling Index
  - Nagle Algorithm control
  - Delayed ACK optimization
  - RSS CPU balancing
  - Receive-Segment Coalescing (RSC)

- **Speedtest Integration**:
  - speedtest-cli para benchmarks
  - Resultados guardados con timestamp
  - Comparación antes/después
  - Export a JSON/CSV

- **Documentation**:
  - README.md completo con diagramas
  - Mermaid architecture diagram
  - Mermaid optimization flow
  - TCP Congestion Control deep-dive
  - CONTRIBUTING.md con guidelines
  - MIT License

- **Project Structure**:
  - Multi-platform support (windows/, linux/ folders)
  - Organized docs/ (optimizations/, diagrams/)
  - GitHub Actions ready (.github/ folder)
  - pyproject.toml configuration

#### 🔧 Configuración
- Requirements.txt con versiones locked
- UTF-8 encoding fixes para Windows
- Logging con colorlog
- Toast notifications (winotify)
- Admin privilege checks

#### 📚 Documentación Técnica
- `tcp-congestion-control.md`: NewReno implementation
- Architecture diagrams con 8 capas
- Optimization flow con rollback paths

### 🐛 Fixes Conocidos
- Python 3.13 venv issues → usar `--copies` flag
- Windows console UTF-8 encoding → forced encoding
- Avast blocking venv → add to exceptions

### ⚠️ Advertencias
- Requiere permisos de Administrador
- Backup automático antes de cambios
- Reboot recomendado después de optimizaciones
- Windows Defender/Antivirus pueden ralentizar primera ejecución

### 📦 Dependencias
```
ttkbootstrap==1.10.1
winotify==1.1.0
colorlog==6.8.2
speedtest-cli==2.1.3
```

### 🔜 Próximas Versiones

#### [1.1.0] - Planeado
- [ ] Linux module completo
- [ ] BBR congestion control (Linux)
- [ ] WSL hybrid mode
- [ ] CLI para scripteo
- [ ] Automated tests (pytest)
- [ ] CI/CD con GitHub Actions

#### [1.2.0] - Planeado
- [ ] Real-time monitoring dashboard
- [ ] Network traffic analysis
- [ ] Per-application optimizations
- [ ] Rollback history (undo stack)
- [ ] Export/import profiles

#### [2.0.0] - Visión
- [ ] macOS support
- [ ] Cloud optimization profiles
- [ ] Machine learning auto-tune
- [ ] Browser extension
- [ ] REST API

---

## Formato de Versiones

### [X.Y.Z]
- **X (Major)**: Cambios incompatibles con versiones anteriores
- **Y (Minor)**: Nuevas funcionalidades (backward-compatible)
- **Z (Patch)**: Bug fixes y mejoras menores

### Categorías
- **Agregado**: Nuevas features
- **Cambiado**: Cambios en funcionalidad existente
- **Deprecado**: Features que serán removidas
- **Removido**: Features eliminadas
- **Corregido**: Bug fixes
- **Seguridad**: Vulnerabilidades corregidas

---

**Última actualización**: 2024-01-20  
**Mantenedor**: LOUST (www.loust.pro)
