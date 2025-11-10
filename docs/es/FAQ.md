# Preguntas Frecuentes (FAQ) - Español

## General

### ¿Qué es NetBoozt?
NetBoozt es un kit de herramientas avanzado de optimización TCP/IP que trae rendimiento de nivel Linux (similar al control de congestión BBR de Google) a Windows. Es 100% open-source y reversible.

### ¿Es seguro?
¡Sí! NetBoozt:
- ✅ Crea backups automáticos antes de cambios
- ✅ 100% reversible con un click
- ✅ Solo modifica el registro de Windows (sin parches binarios)
- ✅ No requiere drivers a nivel kernel
- ✅ Open-source (Licencia MIT)

### ¿Por qué creaste este proyecto?

**Contexto Personal**: Tenía una conexión de fibra de 1 Gbps pero solo obtenía 450-500 Mbps en descargas reales. El problema no era mi ISP, sino el stack TCP de Windows usando algoritmos de 2006 (CUBIC).

**El Descubrimiento**: Linux con BBR obtenía 850-950 Mbps en la misma red. La diferencia era el algoritmo de control de congestión:
- **Windows (CUBIC)**: Reactivo, detecta congestión después de perder paquetes
- **Linux (BBR)**: Proactivo, detecta congestión midiendo RTT antes de pérdidas

**La Solución**: Como Windows no soporta BBR nativamente, creé NetBoozt para optimizar el entorno TCP/IP y lograr resultados similares a BBR sin modificar el kernel.

### ¿Invalidará mi garantía?
No. NetBoozt solo modifica configuraciones del registro de Windows que están oficialmente documentadas por Microsoft. Son las mismas configuraciones que usan los administradores de red.

### ¿Funciona en mi sistema?
**Requisitos:**
- Windows 10/11 (Build 19041+)
- Python 3.10+
- Privilegios de administrador
- Adaptador de red con soporte RSS (la mayoría de adaptadores modernos)

## Rendimiento

### ¿Qué tan rápido será mi internet?
Resultados típicos:
- **Descarga**: +15-20% de mejora
- **Subida**: +10-15% de mejora
- **Latencia**: -12% a -30% de reducción
- **Gaming**: Reducción de picos de lag

Los resultados varían según ISP, condiciones de red y hardware.

### ¿Necesito internet gigabit?
¡No! NetBoozt mejora el rendimiento en cualquier conexión:
- **50 Mbps**: Mejor streaming, menos buffering
- **100 Mbps**: Descargas más rápidas, menor latencia
- **500+ Mbps**: Utilizar todo el ancho de banda, reducir overhead

### ¿Ayudará con gaming?
¡Sí! Beneficios:
- 🎮 Tiempos de ping más bajos
- 📉 Picos de lag reducidos
- ⚡ Procesamiento de paquetes más rápido (RSS)
- 🔄 Mejor manejo de congestión

## Comparación de Algoritmos

### ¿Qué es CUBIC y por qué es problemático?

**CUBIC** es el algoritmo de control de congestión usado por Windows (y Linux pre-BBR):

**Cómo funciona**:
1. Aumenta velocidad exponencialmente
2. Espera hasta que se **pierda un paquete**
3. Asume que la pérdida = congestión
4. Reduce velocidad en ~50%
5. Repite el ciclo

**Problemas**:
- ❌ **Falsos positivos**: Un solo paquete perdido (interferencia WiFi, ruido) causa desaceleración masiva
- ❌ **Alta latencia**: Llena buffers antes de detectar congestión (bufferbloat)
- ❌ **Ineficiente**: Desperdicia ancho de banda al sobrepasar y luego retroceder

**Ejemplo visual**:
```
Velocidad CUBIC:
  ^
  |     /\        /\        /\
  |    /  \      /  \      /  \      ← Picos y valles
  |   /    \    /    \    /    \       constantes
  |  /      \  /      \  /      \
  | /        \/        \/        \
  +--------------------------------> Tiempo
       Pérdida  Pérdida  Pérdida

Resultado: Velocidad inconsistente, latencia alta
```

### ¿Qué es BBR y por qué es mejor?

**BBR** (Bottleneck Bandwidth and RTT) es el algoritmo moderno de Google (2016+):

**Cómo funciona**:
1. Mide continuamente el **ancho de banda** máximo
2. Mide continuamente el **RTT** (Round-Trip Time)
3. Detecta congestión cuando RTT **aumenta** (cola formándose)
4. Mantiene velocidad óptima = `Ancho_de_banda × RTT_mínimo`
5. No espera pérdida de paquetes

**Ventajas**:
- ✅ **Detección temprana**: Ve la congestión antes que CUBIC
- ✅ **Baja latencia**: Evita llenar buffers (anti-bufferbloat)
- ✅ **Tolerante a pérdidas**: Un paquete perdido no causa pánico
- ✅ **Estable**: Mantiene velocidad consistente

**Ejemplo visual**:
```
Velocidad BBR:
  ^
  |  ___________________________
  | /                           \     ← Estable, sin picos
  |/                             \
  +--------------------------------> Tiempo
     Rampeo rápido    Operación estable

Resultado: Velocidad consistente, latencia baja
```

### ¿Cómo logra NetBoozt resultados BBR en Windows?

Windows no puede cambiar su algoritmo de congestión via registro. NetBoozt **optimiza el entorno** para comportarse como BBR:

| Optimización | Cómo ayuda | Equivalente BBR |
|--------------|------------|-----------------|
| **HyStart++** | Slow-start más rápido | Rampeo rápido inicial |
| **PRR** | Recuperación suave de pérdidas | Tolerancia a pérdidas |
| **ECN** | Routers señalan congestión sin perder paquetes | Detección proactiva |
| **TCP Pacing** | Envío suave de paquetes | Evita ráfagas/bufferbloat |
| **Initial RTO** | Recuperación más rápida de timeouts | Menor espera |

**Resultado**: +15-20% throughput, -12% a -30% latencia (similar a BBR real)

[**📖 Comparación técnica completa →**](../optimizations/bbr-vs-cubic.md)

## Instalación

### ¿Por qué mi antivirus lo bloquea?
La creación de venv en Python involucra crear ejecutables, lo cual algunos antivirus marcan. Es un falso positivo.

**Solución**:
```powershell
# Agregar carpeta del proyecto a excepciones del antivirus
# Luego recrear venv:
python -m venv venv --copies
```

### ¿Necesito ejecutar como Administrador?
Sí. Las optimizaciones de red requieren modificaciones del registro que necesitan privilegios de admin.

### ¿Puedo usarlo en WSL?
El soporte WSL está planeado para v1.1.0. Actualmente, NetBoozt optimiza solo el host Windows.

## Uso

### ¿Qué perfil debo usar?
- **🟢 Conservador**: Servidores de producción, estabilidad crítica
- **🟡 Balanceado**: **Recomendado para la mayoría de usuarios**
- **🔴 Agresivo**: Gaming, pruebas, rendimiento máximo

Comienza con Balanceado y actualiza a Agresivo si es estable.

### ¿Necesito reiniciar?
**Recomendado pero no requerido.** Algunas optimizaciones (como RSS) toman efecto inmediatamente, mientras que otras (como TCP Window Scaling) requieren reinicio para efecto completo.

### ¿Cómo hago rollback?
Tres métodos:
1. **GUI**: Click botón "Restore Defaults"
2. **CLI**: `python windows/run.py --reset`
3. **Manual**: Aplicar backup JSON desde `optimizations_backup_*.json`

### ¿Puedo personalizar optimizaciones?
¡Sí! En la GUI:
1. Ve a pestaña "Optimizations"
2. Activa/desactiva optimizaciones individuales
3. Click "Apply Selected"

Para personalización avanzada, edita `windows/src/optimizations/network_optimizer.py`

## Solución de Problemas

### Errores "Access Denied"?
No estás ejecutando como Administrador.

**Solución**:
```powershell
# Click derecho PowerShell → "Ejecutar como Administrador"
cd L:\NetworkFailover\NetBoozt
.\venv\Scripts\Activate.ps1
python windows/run.py
```

### ¿Falla la creación de venv?
Usualmente causado por antivirus bloqueando.

**Solución**:
```powershell
# Agregar carpeta a excepciones del antivirus, luego:
python -m venv venv --copies
```

### ¿La GUI no abre?
Verifica dependencias:
```powershell
pip install -r windows/requirements.txt

# Verificar ttkbootstrap:
python -c "import ttkbootstrap; print('OK')"
```

### ¿Speed test no funciona?
Instala speedtest-cli:
```powershell
pip install speedtest-cli

# Prueba manualmente:
speedtest-cli
```

### ¿Sin mejora de rendimiento?
Checklist:
1. ✅ ¿Reiniciaste después de aplicar optimizaciones?
2. ✅ ¿Usaste el perfil correcto? (prueba Agresivo)
3. ✅ ¿Tu adaptador soporta RSS?
4. ✅ ¿Tu ISP no está limitando?

Ejecuta speed tests antes/después para medir:
```powershell
# Antes de optimización
speedtest-cli > antes.txt

# Aplicar optimizaciones + reiniciar

# Después de optimización
speedtest-cli > despues.txt
```

## Soporte

### ¿Dónde obtengo ayuda?
- **GitHub Issues**: [Reportar bugs](https://github.com/louzt/NetBoozt_InternetUpgrade/issues)
- **Discussions**: [Preguntas e ideas](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions)
- **Email**: opensource@loust.pro

### ¿Cómo reporto bugs?
[Abrir un issue](https://github.com/louzt/NetBoozt_InternetUpgrade/issues/new) con:
1. Versión de Windows
2. Versión de Python
3. Mensaje de error/logs
4. Pasos para reproducir

### ¿Cómo solicito features?
[Iniciar una discusión](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions/new) describiendo:
1. Descripción del feature
2. Caso de uso
3. Beneficio esperado

---

**¿Aún tienes preguntas?** [Pregunta en GitHub Discussions](https://github.com/louzt/NetBoozt_InternetUpgrade/discussions) 💬
