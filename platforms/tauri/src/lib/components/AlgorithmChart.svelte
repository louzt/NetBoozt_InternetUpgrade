<!--
    AlgorithmChart.svelte - Visualización de algoritmos de congestión TCP
    Muestra gráficas animadas de CUBIC vs BBR-like
    By LOUST
-->
<script lang="ts">
    import { onMount } from 'svelte';
    
    export let algorithm: 'cubic' | 'bbr-like' = 'cubic';
    export let animated = true;
    export let compact = false;
    
    let animationProgress = animated ? 0 : 1;
    let animationFrame: number;
    let mounted = false;
    
    const width = compact ? 260 : 280;
    const height = compact ? 100 : 120;
    const padding = 15;
    
    // Datos para CUBIC (sube, cae por pérdida, sube lento)
    function generateCubicPath(): string {
        const points: [number, number][] = [];
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        let y = 0.2; // Empezar bajo
        let phase = 'ramp'; // ramp, loss, recovery
        let t = 0;
        let wMax = 0.9;
        
        for (let x = 0; x <= chartWidth; x += 2) {
            const normalizedX = x / chartWidth;
            
            // Simular comportamiento CUBIC
            if (normalizedX < 0.25) {
                // Ramp up exponencial
                y = 0.2 + (normalizedX / 0.25) * 0.7;
            } else if (normalizedX < 0.3) {
                // Packet loss - caída brusca
                const lossProgress = (normalizedX - 0.25) / 0.05;
                y = 0.9 - lossProgress * 0.45; // Baja 50%
            } else if (normalizedX < 0.55) {
                // Recovery lenta (función cúbica)
                const recoveryProgress = (normalizedX - 0.3) / 0.25;
                y = 0.45 + Math.pow(recoveryProgress, 3) * 0.45;
            } else if (normalizedX < 0.6) {
                // Otra pérdida
                const lossProgress = (normalizedX - 0.55) / 0.05;
                y = 0.9 - lossProgress * 0.4;
            } else {
                // Recovery final
                const recoveryProgress = (normalizedX - 0.6) / 0.4;
                y = 0.5 + Math.pow(recoveryProgress, 2) * 0.4;
            }
            
            // Aplicar límites de animación
            if (animated && normalizedX > animationProgress) {
                break;
            }
            
            const screenY = padding + chartHeight * (1 - y);
            points.push([x + padding, screenY]);
        }
        
        if (points.length < 2) return '';
        
        return `M ${points.map(p => p.join(',')).join(' L ')}`;
    }
    
    // Datos para BBR-like (sube rápido, estable, tolera pérdidas)
    function generateBBRPath(): string {
        const points: [number, number][] = [];
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        for (let x = 0; x <= chartWidth; x += 2) {
            const normalizedX = x / chartWidth;
            let y: number;
            
            if (normalizedX < 0.15) {
                // Fast ramp up
                y = 0.2 + (normalizedX / 0.15) * 0.7;
            } else if (normalizedX < 0.3) {
                // Pequeño ajuste al encontrar óptimo
                const adjust = Math.sin((normalizedX - 0.15) * Math.PI * 4) * 0.05;
                y = 0.88 + adjust;
            } else {
                // Estable con pequeñas variaciones
                const noise = Math.sin(normalizedX * 20) * 0.02;
                y = 0.88 + noise;
                
                // Simular pérdida de paquete sin caída
                if (normalizedX > 0.5 && normalizedX < 0.52) {
                    // BBR no cae por pérdidas aisladas
                    y = 0.86;
                }
            }
            
            if (animated && normalizedX > animationProgress) {
                break;
            }
            
            const screenY = padding + chartHeight * (1 - y);
            points.push([x + padding, screenY]);
        }
        
        if (points.length < 2) return '';
        
        return `M ${points.map(p => p.join(',')).join(' L ')}`;
    }
    
    $: path = algorithm === 'cubic' ? generateCubicPath() : generateBBRPath();
    $: color = algorithm === 'cubic' ? '#FFC107' : '#00d4aa';
    
    onMount(() => {
        mounted = true;
        if (animated) {
            animationProgress = 0;
            const animate = () => {
                animationProgress += 0.02;
                if (animationProgress < 1) {
                    animationFrame = requestAnimationFrame(animate);
                } else {
                    animationProgress = 1;
                }
            };
            // Pequeño delay para asegurar que el componente esté listo
            setTimeout(() => {
                animationFrame = requestAnimationFrame(animate);
            }, 100);
            
            return () => {
                if (animationFrame) cancelAnimationFrame(animationFrame);
            };
        } else {
            animationProgress = 1;
        }
    });
    
    function restart() {
        animationProgress = 0;
        if (animated) {
            const animate = () => {
                animationProgress += 0.015;
                if (animationProgress < 1) {
                    animationFrame = requestAnimationFrame(animate);
                } else {
                    animationProgress = 1;
                }
            };
            animationFrame = requestAnimationFrame(animate);
        }
    }
    
    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter' || event.key === ' ') {
            restart();
        }
    }
</script>

<div class="chart-container" class:compact on:click={restart} on:keydown={handleKeydown} role="button" tabindex="0" title="Click para reiniciar animación">
    <svg {width} {height} viewBox="0 0 {width} {height}">
        <!-- Grid -->
        <defs>
            <pattern id="grid-{algorithm}" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#3d3d3d" stroke-width="0.5" opacity="0.3"></path>
            </pattern>
        </defs>
        <rect x={padding} y={padding} width={width - padding * 2} height={height - padding * 2} fill="url(#grid-{algorithm})"/>
        
        <!-- Eje Y label -->
        <text x="3" y={height/2} fill="var(--text-muted, #666)" font-size="8" text-anchor="middle" transform="rotate(-90, 3, {height/2})">
            Velocidad
        </text>
        
        <!-- Eje X label -->
        <text x={width/2} y={height - 2} fill="var(--text-muted, #666)" font-size="8" text-anchor="middle">
            Tiempo
        </text>
        
        <!-- Línea del gráfico -->
        {#if path}
            <path 
                d={path} 
                fill="none" 
                stroke={color} 
                stroke-width="3" 
                stroke-linecap="round"
                stroke-linejoin="round"
                class="chart-line"
            />
        {/if}
        
        <!-- Markers de eventos -->
        {#if algorithm === 'cubic' && animationProgress > 0.25}
            <g class="event-marker">
                <circle cx={padding + (width - padding * 2) * 0.27} cy={height * 0.15} r="8" fill="rgba(255, 68, 68, 0.2)"/>
                <text x={padding + (width - padding * 2) * 0.27} y={height * 0.15 + 3} fill="#ff4444" font-size="8" text-anchor="middle">📉</text>
            </g>
        {/if}
        
        {#if algorithm === 'cubic' && animationProgress > 0.55}
            <g class="event-marker">
                <circle cx={padding + (width - padding * 2) * 0.57} cy={height * 0.15} r="8" fill="rgba(255, 68, 68, 0.2)"/>
                <text x={padding + (width - padding * 2) * 0.57} y={height * 0.15 + 3} fill="#ff4444" font-size="8" text-anchor="middle">📉</text>
            </g>
        {/if}
        
        {#if algorithm === 'bbr-like' && animationProgress > 0.5}
            <g class="event-marker">
                <circle cx={padding + (width - padding * 2) * 0.51} cy={height * 0.15} r="8" fill="rgba(0, 212, 170, 0.2)"/>
                <text x={padding + (width - padding * 2) * 0.51} y={height * 0.15 + 3} fill="#00d4aa" font-size="8" text-anchor="middle">✓</text>
            </g>
        {/if}
    </svg>
    
    <div class="chart-legend">
        <span class="legend-dot" style="background: {color}"></span>
        <span class="legend-text">
            {#if algorithm === 'cubic'}
                CUBIC: Cae ~50% por pérdida
            {:else}
                BBR-like: Estable, tolera pérdidas
            {/if}
        </span>
    </div>
</div>

<style>
    .chart-container {
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        padding: 0.5rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .chart-container:hover {
        background: var(--bg-hover, #333);
    }
    
    .chart-container.compact {
        padding: 0.35rem;
    }
    
    svg {
        display: block;
    }
    
    .chart-line {
        filter: drop-shadow(0 0 4px currentColor);
    }
    
    .event-marker {
        animation: pulse 1s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .chart-legend {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin-top: 0.35rem;
        padding-top: 0.35rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .legend-text {
        font-size: 0.65rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .compact .chart-legend {
        display: flex;
        padding-top: 0.25rem;
        margin-top: 0.25rem;
    }
    
    .compact .legend-text {
        font-size: 0.6rem;
    }
</style>
