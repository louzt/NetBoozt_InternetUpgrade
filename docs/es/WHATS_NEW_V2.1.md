# 🎉 Novedades en NetBoozt v2.1

## 🚀 Características Principales

### 1. Sistema de DNS Auto-Failover 🔄

**Cambio automático de tier DNS con monitoreo de salud**

- ✅ **Health checks en tiempo real** cada 15 segundos
- ✅ **Failover automático** cuando el tier actual falla
- ✅ **Cooldown de 60 segundos** para prevenir flapping
- ✅ **7 tiers DNS** con fallback inteligente
- ✅ **Notificaciones de Windows** en eventos de failover

**Cómo funciona:**
```
Cloudflare (1.1.1.1) ─┐
                      ├─► Health Checker (ping cada 15s)
Google (8.8.8.8) ─────┤
                      │
Quad9 (9.9.9.9) ──────┤   ¿Tier DOWN? ──► Auto-cambio a siguiente tier saludable
                      │
OpenDNS ──────────────┤
                      │
... 7 tiers total ────┘
```

**Beneficios:**
- Nunca pierdas internet por caídas de DNS del ISP
- Resolución DNS más rápida (frecuentemente más rápido que DNS del ISP)
- Recuperación automática sin intervención manual
- Indicadores visuales en GUI (🟢 ACTIVO / 🟡 LENTO / 🔴 CAÍDO)

**Uso:**
1. Ve a la pestaña **"Failover DNS"**
2. Activa el switch **"Auto-Failover"**
3. El sistema monitorea automáticamente
4. Recibe notificaciones cuando cambia el tier

---

### 2. Sistema de Alertas Inteligente 🔔

**Monitoreo proactivo de red con umbrales configurables**

- ✅ **6 tipos de alerta**: Latencia, Pérdida de Paquetes, Velocidad, DNS, Adaptador, Memoria
- ✅ **Umbrales configurables** por tipo de alerta
- ✅ **Auto-resolución** cuando métricas vuelven a normalidad
- ✅ **Historial de alertas** con estadísticas
- ✅ **Períodos de cooldown** para prevenir spam de notificaciones
- ✅ **Notificaciones toast de Windows**

**Tipos de Alerta:**

| Alerta | Umbral por Defecto | Severidad |
|--------|-------------------|-----------|
| Latencia Alta | 100ms | Advertencia |
| Pérdida de Paquetes Alta | 2% | Crítico |
| Velocidad Baja | 10 Mbps | Advertencia |
| Falla DNS | 3 fallos consecutivos | Crítico |
| Errores de Adaptador | 10 errores/min | Advertencia |
| Memoria Alta | 80% uso | Info |

**Flujo de Ejemplo:**
```
Latencia: 120ms (excede umbral de 100ms)
    ↓
Alerta disparada → Notificación toast
    ↓
Latencia baja a 50ms
    ↓
Alerta auto-resuelta
```

**Uso:**
1. Ve a la pestaña **"Alertas"**
2. Configura umbrales para cada métrica
3. Click **"Guardar Configuración"**
4. El sistema monitorea automáticamente
5. Ver alertas activas e historial

---

### 3. Sistema de Backups de Configuración 💾

**Snapshots de un click de configuración de red**

- ✅ **Snapshots instantáneos** de configuración DNS, IP, TCP, Registry
- ✅ **Restauración de un click** a cualquier estado previo
- ✅ **Limpieza automática** (mantiene últimos 50 backups)
- ✅ **Export/import JSON** para compartir configs
- ✅ **Pre-backup antes de optimizaciones** (seguridad primero)

**Lo que se respalda:**
```json
{
  "backup_id": "20251110_164030",
  "timestamp": "2025-11-10T16:40:30",
  "adapter_name": "Ethernet",
  "dns_servers": ["1.1.1.1", "1.0.0.1"],
  "ip_config": {
    "IPv4Address": "192.168.1.100",
    "SubnetMask": "255.255.255.0",
    "DefaultGateway": "192.168.1.1"
  },
  "tcp_settings": {
    "AutoTuningLevel": "normal",
    "Timestamps": "enabled",
    "ECN": "enabled"
  },
  "registry_values": {
    "TcpWindowSize": 65535,
    "NetworkThrottlingIndex": 4294967295
  }
}
```

**Uso:**
1. Ve a la pestaña **"Backups"**
2. Click **"Crear Backup Ahora"**
3. Para restaurar: selecciona backup → click **"Restaurar"**
4. Para eliminar: selecciona backup → click **"Eliminar"**

**Casos de uso:**
- Antes de cambiar configuración de red
- Antes de aplicar optimizaciones
- Probar diferentes configuraciones DNS
- Compartir configuración con otros PCs
- Recuperación ante desastres

---

### 4. Gráficas de Monitoreo Avanzadas 📊

**Analíticas de red profesionales con matplotlib**

- ✅ **4 gráficas en tiempo real**: Descarga, Subida, Latencia, Pérdida de Paquetes
- ✅ **Zoom temporal**: 5min, 15min, 30min, 1h, 6h, 24h, 7 días
- ✅ **Integración con Matplotlib** con tema oscuro
- ✅ **Formateo automático de ejes**
- ✅ **Actualizaciones en tiempo real**

**Gráficas disponibles:**

| Gráfica | Métrica | Color | Rango Temporal |
|---------|---------|-------|----------------|
| Velocidad de Descarga | Mbps | Verde | 5min - 7 días |
| Velocidad de Subida | Mbps | Morado | 5min - 7 días |
| Latencia | ms | Amarillo | 5min - 7 días |
| Pérdida de Paquetes | % | Rojo | 5min - 7 días |

**Características:**
- Zoom temporal con dropdown selector
- Actualización automática cada 5 segundos
- Integración con tema oscuro/claro
- Formateo inteligente de ejes (K/M para grandes números)
- Almacenamiento eficiente (estrategia 3-2-1)

**Estrategia de Almacenamiento 3-2-1:**
```
Últimas 24h    : TODOS los datos (granularidad completa)
1-7 días       : 1 muestra/hora (agregada)
8-30 días      : 1 muestra/día (agregada)
30+ días       : 1 muestra/semana (agregada)
```

**Uso:**
1. Ve a la pestaña **"Gráficas"**
2. Selecciona rango temporal en dropdown
3. Las gráficas se actualizan automáticamente
4. Observa patrones y tendencias

**Casos de uso:**
- Detectar throttling del ISP
- Identificar patrones de latencia
- Monitorear pérdida de paquetes
- Analizar tendencias de velocidad
- Optimización de red basada en datos

---

### 5. Sistema de Temas Dark/Light 🎨

**Interfaz profesional con cambio de tema instantáneo**

- ✅ **Dos temas completos** con paletas de color coherentes
- ✅ **Cambio instantáneo** sin reiniciar
- ✅ **Sistema de callbacks** para actualizaciones dinámicas
- ✅ **Integración con CustomTkinter**
- ✅ **Preferencia persistente** (guardada en configuración)

**Tema Oscuro:**
```
Fondo: #1a1a1a
Cards: #2b2b2b
Texto: #ffffff
Accent: #00d4aa
```

**Tema Claro:**
```
Fondo: #f0f0f0
Cards: #ffffff
Texto: #1a1a1a
Accent: #0078d4
```

**Uso:**
1. Ve a la pestaña **"Settings"**
2. Click en botón **"Toggle Theme"**
3. El tema cambia instantáneamente
4. Preferencia guardada automáticamente

---

## 🔧 Mejoras del Sistema

### Optimizaciones de GUI
- **12 pestañas** de navegación (Dashboard, Optimizaciones, Estado, Failover, Gráficas, Alertas, Backups, Configuración, Acerca de, README, Docs, GitHub)
- **Operaciones en background** (no bloquea UI)
- **Cache de estado** de optimizaciones (inicio más rápido)
- **Callbacks apropiados** para todos los monitores

### Calidad de Código
- Reemplazados 26 `print` con logging apropiado
- Corregidos 10 bloques `except:` con excepciones específicas
- Agregada thread safety con `Lock`
- Corregidas memory leaks en `NetworkMonitor`
- Manejadores de limpieza apropiados (`__del__`, `on_closing`)

### Rendimiento
- Control de loop del dashboard (previene múltiples loops concurrentes)
- Sistema de cache para detección de optimizaciones
- Almacenamiento eficiente de datos (estrategia 3-2-1)
- Threads de background para todas las operaciones de red

---

## 📦 Nuevas Dependencias

```
winotify>=1.1.0      # Notificaciones toast de Windows (opcional)
matplotlib>=3.7.0    # Gráficas avanzadas
```

---

## 🎯 Estadísticas v2.1

- **Líneas de Código**: 9,300+ (Python)
- **Nuevos Módulos**: 8
- **Nuevas Funciones**: 100+
- **Nuevos Componentes GUI**: 200+
- **Cobertura de Código**: ~75% (estimado)

---

## 🚀 Cómo Migrar de v1.0 a v2.1

### 1. Actualizar Dependencias
```powershell
cd L:\NetworkFailover\NetBoozt\windows
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt --upgrade
pip install winotify  # Opcional para notificaciones
```

### 2. Crear Backup
1. Abre NetBoozt v1.0
2. Ve a pestaña "Backups" (nueva)
3. Click "Crear Backup Ahora"
4. Guarda el archivo JSON generado

### 3. Actualizar Código
```powershell
git pull origin main
# O descarga la release v2.1.0
```

### 4. Ejecutar v2.1
```powershell
python run.py
```

### 5. Explorar Nuevas Características
- Habilita **Auto-Failover** en pestaña DNS
- Configura **Alertas** con tus umbrales preferidos
- Crea **Backup** de tu configuración actual
- Explora **Gráficas** con diferentes rangos temporales
- Prueba **Dark/Light Theme** en Configuración

---

## 🔜 Roadmap

### v2.2 (Planeado)
- [ ] Optimizaciones por aplicación
- [ ] Análisis de tráfico de red
- [ ] Historial de rollback (undo stack)
- [ ] Import/export de perfiles
- [ ] Suite de testing automatizado (pytest)

### v3.0 (Visión)
- [ ] Auto-tuning con machine learning
- [ ] API REST para gestión remota
- [ ] Dashboard web
- [ ] Soporte para macOS
- [ ] Perfiles de optimización cloud

---

## 🙏 Agradecimientos

NetBoozt v2.1 ha sido posible gracias a:
- **Google BBR** - Inspiración del algoritmo de control de congestión
- **CustomTkinter** - Framework de GUI moderna
- **Matplotlib** - Librería profesional de gráficas
- **winotify** - Notificaciones toast de Windows
- **Comunidad de usuarios** - Feedback y bug reports

---

<div align="center">

**Hecho con ❤️ por [LOUST](https://www.loust.pro)**

[🐛 Reportar Bug](https://github.com/louzt/NetBoozt_InternetUpgrade/issues) • [💡 Sugerir Característica](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)

</div>
