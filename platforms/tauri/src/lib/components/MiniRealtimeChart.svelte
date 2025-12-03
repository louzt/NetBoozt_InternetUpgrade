<!--
    MiniRealtimeChart.svelte - Gráfica compacta de datos en tiempo real
    Con tooltips interactivos y diseño responsivo
    Sin dependencias externas, usa Canvas nativo
    By LOUST
-->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import Icon from './Icon.svelte';
    
    // Props
    export let title = 'Métrica';
    export let unit = '';
    export let icon: string = 'activity';
    export let color = '#00d4aa';
    export let data: number[] = [];
    export let maxPoints = 30;
    export let currentValue: number = 0;
    export let compact = false; // Modo compacto para pantallas pequeñas
    
    let canvasEl: HTMLCanvasElement;
    let containerEl: HTMLDivElement;
    let ctx: CanvasRenderingContext2D | null = null;
    
    // Dimensiones responsivas - aumentado para mejor visualización
    let width = 280;
    let height = 100;
    const padding = { top: 10, right: 10, bottom: 18, left: 35 };
    
    // Tooltip state
    let tooltipVisible = false;
    let tooltipX = 0;
    let tooltipY = 0;
    let tooltipValue = 0;
    let tooltipIndex = 0;
    
    // Puntos calculados para interacción
    let calculatedPoints: [number, number, number][] = []; // [x, y, value]
    
    // Stats
    $: dataSlice = data.slice(-maxPoints);
    $: stats = {
        min: dataSlice.length > 0 ? Math.min(...dataSlice) : 0,
        max: dataSlice.length > 0 ? Math.max(...dataSlice) : 100,
        avg: dataSlice.length > 0 ? dataSlice.reduce((a, b) => a + b, 0) / dataSlice.length : 0
    };
    
    // Formatear valores grandes
    function formatValue(val: number): string {
        if (val >= 1000) {
            return (val / 1000).toFixed(1) + 'K';
        }
        if (val >= 100) {
            return val.toFixed(0);
        }
        return val.toFixed(1);
    }
    
    // Tiempo relativo para tooltip
    function getTimeAgo(index: number, total: number): string {
        const secondsAgo = (total - index - 1);
        if (secondsAgo === 0) return 'Ahora';
        if (secondsAgo === 1) return 'Hace 1s';
        return `Hace ${secondsAgo}s`;
    }
    
    function draw() {
        if (!ctx || !canvasEl) return;
        
        const c = ctx;
        const dpr = window.devicePixelRatio || 1;
        
        c.clearRect(0, 0, width * dpr, height * dpr);
        c.save();
        c.scale(dpr, dpr);
        
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        
        // Grid
        c.strokeStyle = 'rgba(100, 100, 100, 0.15)';
        c.lineWidth = 0.5;
        for (let i = 0; i <= 3; i++) {
            const y = padding.top + (chartHeight / 3) * i;
            c.beginPath();
            c.moveTo(padding.left, y);
            c.lineTo(width - padding.right, y);
            c.stroke();
        }
        
        if (dataSlice.length < 2) {
            c.fillStyle = '#555';
            c.font = '10px sans-serif';
            c.textAlign = 'center';
            c.fillText('Sin datos', width / 2, height / 2);
            c.restore();
            calculatedPoints = [];
            return;
        }
        
        // Rango dinámico
        const range = stats.max - stats.min || 1;
        const minY = Math.max(0, stats.min - range * 0.1);
        const maxY = stats.max + range * 0.1;
        
        // Labels Y
        c.fillStyle = '#666';
        c.font = '8px sans-serif';
        c.textAlign = 'right';
        c.textBaseline = 'middle';
        c.fillText(formatValue(maxY), padding.left - 4, padding.top);
        c.fillText(formatValue(minY), padding.left - 4, height - padding.bottom);
        
        // Calcular puntos
        const points: [number, number][] = dataSlice.map((value, index) => {
            const x = padding.left + (index / (maxPoints - 1)) * chartWidth;
            const normalized = (value - minY) / (maxY - minY || 1);
            const y = padding.top + chartHeight * (1 - Math.max(0, Math.min(1, normalized)));
            return [x, y];
        });
        
        // Guardar puntos con valores para tooltip
        calculatedPoints = dataSlice.map((value, index) => {
            const x = padding.left + (index / (maxPoints - 1)) * chartWidth;
            const normalized = (value - minY) / (maxY - minY || 1);
            const y = padding.top + chartHeight * (1 - Math.max(0, Math.min(1, normalized)));
            return [x, y, value] as [number, number, number];
        });
        
        // Área con gradiente
        c.beginPath();
        c.moveTo(points[0][0], padding.top + chartHeight);
        points.forEach(([x, y]) => c.lineTo(x, y));
        c.lineTo(points[points.length - 1][0], padding.top + chartHeight);
        c.closePath();
        
        const gradient = c.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        gradient.addColorStop(0, `${color}30`);
        gradient.addColorStop(1, 'transparent');
        c.fillStyle = gradient;
        c.fill();
        
        // Línea principal
        c.beginPath();
        c.moveTo(points[0][0], points[0][1]);
        points.forEach(([x, y]) => c.lineTo(x, y));
        c.strokeStyle = color;
        c.lineWidth = 1.5;
        c.lineCap = 'round';
        c.lineJoin = 'round';
        c.stroke();
        
        // Punto actual (último)
        const last = points[points.length - 1];
        c.beginPath();
        c.arc(last[0], last[1], 3, 0, Math.PI * 2);
        c.fillStyle = color;
        c.fill();
        
        // Efecto glow en el último punto
        c.beginPath();
        c.arc(last[0], last[1], 6, 0, Math.PI * 2);
        c.fillStyle = `${color}20`;
        c.fill();
        
        c.restore();
    }
    
    function handleMouseMove(e: MouseEvent) {
        if (!canvasEl || calculatedPoints.length < 2) return;
        
        const rect = canvasEl.getBoundingClientRect();
        const scaleX = width / rect.width; // Escala para canvas responsivo
        const scaleY = height / rect.height;
        const x = (e.clientX - rect.left) * scaleX;
        const y = (e.clientY - rect.top) * scaleY;
        
        // Encontrar el punto más cercano con detección mejorada
        let closestDist = Infinity;
        let closestIndex = -1;
        const threshold = 35; // Radio de detección aumentado para mejor UX
        
        calculatedPoints.forEach(([px, py, _], index) => {
            // Priorizar distancia horizontal para gráficas temporales
            const distX = Math.abs(px - x);
            const distY = Math.abs(py - y);
            const dist = Math.sqrt(distX ** 2 + (distY * 0.5) ** 2); // Y tiene menos peso
            
            if (dist < closestDist && distX < threshold) {
                closestDist = dist;
                closestIndex = index;
            }
        });
        
        if (closestIndex >= 0) {
            const [px, py, value] = calculatedPoints[closestIndex];
            tooltipVisible = true;
            tooltipX = px;
            tooltipY = py;
            tooltipValue = value;
            tooltipIndex = closestIndex;
        } else {
            tooltipVisible = false;
        }
    }
    
    function handleMouseLeave() {
        tooltipVisible = false;
    }
    
    // Resize observer para responsividad
    function handleResize() {
        if (!containerEl) return;
        const containerWidth = containerEl.clientWidth;
        
        // Ajustar width al contenedor
        width = Math.max(200, Math.min(containerWidth - 20, 320));
        height = compact ? 70 : 100; // Altura aumentada para mejor visualización
        
        if (canvasEl && ctx) {
            const dpr = window.devicePixelRatio || 1;
            canvasEl.width = width * dpr;
            canvasEl.height = height * dpr;
            draw();
        }
    }
    
    $: if (data && ctx) {
        draw();
    }
    
    onMount(() => {
        if (canvasEl) {
            const dpr = window.devicePixelRatio || 1;
            canvasEl.width = width * dpr;
            canvasEl.height = height * dpr;
            ctx = canvasEl.getContext('2d');
            draw();
        }
        
        // Observador de resize
        if (containerEl && typeof ResizeObserver !== 'undefined') {
            const observer = new ResizeObserver(handleResize);
            observer.observe(containerEl);
            return () => observer.disconnect();
        }
    });
</script>

<div class="mini-chart" class:compact bind:this={containerEl}>
    <div class="header">
        <div class="label">
            <Icon name={icon} size={compact ? 10 : 12} color={color} />
            <span>{title}</span>
        </div>
        <div class="value-container" title="{currentValue.toFixed(2)} {unit}">
            <span class="value" style="color: {color}">{formatValue(currentValue)}</span>
            <span class="unit">{unit}</span>
        </div>
    </div>
    
    <div class="canvas-container">
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <canvas 
            bind:this={canvasEl}
            style="width: {width}px; height: {height}px;"
            on:mousemove={handleMouseMove}
            on:mouseleave={handleMouseLeave}
            aria-label="Gráfica de {title}: valor actual {currentValue.toFixed(1)} {unit}"
        />
        
        <!-- Tooltip -->
        {#if tooltipVisible}
            <div 
                class="tooltip" 
                style="left: {tooltipX}px; top: {tooltipY - 35}px; border-color: {color};"
            >
                <div class="tooltip-value" style="color: {color}">
                    {formatValue(tooltipValue)} {unit}
                </div>
                <div class="tooltip-time">
                    {getTimeAgo(tooltipIndex, calculatedPoints.length)}
                </div>
            </div>
            <div 
                class="tooltip-dot" 
                style="left: {tooltipX}px; top: {tooltipY}px; background: {color}; box-shadow: 0 0 8px {color};"
            />
        {/if}
    </div>
    
    <div class="stats-bar">
        <div class="stat" title="Valor mínimo: {stats.min.toFixed(2)} {unit}">
            <span class="stat-label">Min</span>
            <span class="stat-value">{formatValue(stats.min)}</span>
        </div>
        <div class="stat avg" title="Valor promedio: {stats.avg.toFixed(2)} {unit}">
            <span class="stat-label">Prom</span>
            <span class="stat-value">{formatValue(stats.avg)}</span>
        </div>
        <div class="stat" title="Valor máximo: {stats.max.toFixed(2)} {unit}">
            <span class="stat-label">Max</span>
            <span class="stat-value">{formatValue(stats.max)}</span>
        </div>
    </div>
</div>

<style>
    .mini-chart {
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 0.65rem;
        transition: all 0.15s;
        min-width: 200px;
        flex: 1;
    }
    
    .mini-chart.compact {
        padding: 0.5rem;
        min-width: 160px;
    }
    
    .mini-chart:hover {
        background: var(--bg-hover, #333);
        border-color: rgba(255, 255, 255, 0.1);
    }
    
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        padding-bottom: 0.35rem;
        border-bottom: 1px solid var(--border, rgba(255, 255, 255, 0.06));
        flex-wrap: wrap;
        gap: 0.25rem;
    }
    
    .label {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.6875rem;
        font-weight: 600;
        color: var(--text-muted, #888);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .compact .label {
        font-size: 0.625rem;
    }
    
    .value-container {
        display: flex;
        align-items: baseline;
        gap: 0.2rem;
        cursor: help;
    }
    
    .value {
        font-size: 1rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .compact .value {
        font-size: 0.875rem;
    }
    
    .unit {
        font-size: 0.65rem;
        font-weight: 500;
        color: var(--text-muted, #666);
    }
    
    .canvas-container {
        position: relative;
        width: 100%;
    }
    
    canvas {
        display: block;
        border-radius: 6px;
        background: rgba(0, 0, 0, 0.2);
        cursor: crosshair;
        width: 100% !important;
        max-width: 100%;
    }
    
    /* Tooltip styles */
    .tooltip {
        position: absolute;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid;
        border-radius: 6px;
        padding: 0.35rem 0.5rem;
        pointer-events: none;
        z-index: 100;
        transform: translateX(-50%);
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    
    .tooltip::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 50%;
        transform: translateX(-50%);
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid var(--bg-card, #1a1a1a);
    }
    
    .tooltip-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.75rem;
    }
    
    .tooltip-time {
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        text-align: center;
    }
    
    .tooltip-dot {
        position: absolute;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        pointer-events: none;
        z-index: 99;
    }
    
    /* Stats bar at bottom */
    .stats-bar {
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
        padding-top: 0.35rem;
        border-top: 1px solid var(--border, rgba(255, 255, 255, 0.06));
        font-size: 0.5625rem;
        color: var(--text-muted, #666);
    }
    
    .compact .stats-bar {
        margin-top: 0.35rem;
        padding-top: 0.25rem;
    }
    
    .stat {
        display: flex;
        align-items: center;
        gap: 0.2rem;
        cursor: help;
        padding: 0.15rem 0.25rem;
        border-radius: 3px;
        transition: background 0.15s;
    }
    
    .stat:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    .stat.avg {
        color: var(--accent, #00d4aa);
    }
    
    .stat-label {
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .stat-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
    }
    
    /* Responsive adjustments */
    @media (max-width: 600px) {
        .mini-chart {
            min-width: 140px;
            padding: 0.5rem;
        }
        
        .header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.25rem;
        }
        
        .value {
            font-size: 0.875rem;
        }
        
        .stats-bar {
            font-size: 0.5rem;
        }
    }
</style>
