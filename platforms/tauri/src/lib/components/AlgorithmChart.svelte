<!--
    AlgorithmChart.svelte - Visualización de algoritmos de congestión TCP
    Muestra gráficas animadas de CUBIC vs BBR-like
    By LOUST
-->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    
    export let algorithm: 'cubic' | 'bbr-like' = 'cubic';
    export let animated = true;
    export let compact = false;
    
    let animationProgress = 1; // Empezar completo, animar después
    let animationFrame: number | null = null;
    let canvasEl: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D | null = null;
    
    const width = compact ? 260 : 280;
    const height = compact ? 100 : 120;
    const padding = 20;
    
    // Colores
    $: color = algorithm === 'cubic' ? '#FFC107' : '#00d4aa';
    $: bgColor = algorithm === 'cubic' ? 'rgba(255, 193, 7, 0.1)' : 'rgba(0, 212, 170, 0.1)';
    
    // Genera puntos para CUBIC
    function generateCubicPoints(): [number, number][] {
        const points: [number, number][] = [];
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        for (let x = 0; x <= chartWidth; x += 2) {
            const normalizedX = x / chartWidth;
            let y: number;
            
            if (normalizedX < 0.25) {
                y = 0.15 + (normalizedX / 0.25) * 0.75;
            } else if (normalizedX < 0.3) {
                const lossProgress = (normalizedX - 0.25) / 0.05;
                y = 0.9 - lossProgress * 0.45;
            } else if (normalizedX < 0.55) {
                const recoveryProgress = (normalizedX - 0.3) / 0.25;
                y = 0.45 + Math.pow(recoveryProgress, 3) * 0.45;
            } else if (normalizedX < 0.6) {
                const lossProgress = (normalizedX - 0.55) / 0.05;
                y = 0.9 - lossProgress * 0.4;
            } else {
                const recoveryProgress = (normalizedX - 0.6) / 0.4;
                y = 0.5 + Math.pow(recoveryProgress, 2) * 0.4;
            }
            
            const screenX = padding + x;
            const screenY = padding + chartHeight * (1 - y);
            points.push([screenX, screenY]);
        }
        
        return points;
    }
    
    // Genera puntos para BBR-like
    function generateBBRPoints(): [number, number][] {
        const points: [number, number][] = [];
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        for (let x = 0; x <= chartWidth; x += 2) {
            const normalizedX = x / chartWidth;
            let y: number;
            
            if (normalizedX < 0.15) {
                y = 0.15 + (normalizedX / 0.15) * 0.73;
            } else if (normalizedX < 0.25) {
                const adjust = Math.sin((normalizedX - 0.15) * Math.PI * 6) * 0.04;
                y = 0.88 + adjust;
            } else {
                const noise = Math.sin(normalizedX * 25) * 0.015;
                y = 0.88 + noise;
                
                if (normalizedX > 0.5 && normalizedX < 0.53) {
                    y = 0.85;
                }
            }
            
            const screenX = padding + x;
            const screenY = padding + chartHeight * (1 - y);
            points.push([screenX, screenY]);
        }
        
        return points;
    }
    
    function draw() {
        if (!ctx || !canvasEl) return;
        
        // Variable local para TypeScript
        const c = ctx;
        
        const dpr = window.devicePixelRatio || 1;
        c.clearRect(0, 0, width * dpr, height * dpr);
        c.save();
        c.scale(dpr, dpr);
        
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        // Fondo del área del gráfico
        c.fillStyle = 'rgba(60, 60, 60, 0.3)';
        c.fillRect(padding, padding, chartWidth, chartHeight);
        
        // Grid
        c.strokeStyle = 'rgba(100, 100, 100, 0.3)';
        c.lineWidth = 0.5;
        for (let x = padding; x <= width - padding; x += 25) {
            c.beginPath();
            c.moveTo(x, padding);
            c.lineTo(x, height - padding);
            c.stroke();
        }
        for (let y = padding; y <= height - padding; y += 20) {
            c.beginPath();
            c.moveTo(padding, y);
            c.lineTo(width - padding, y);
            c.stroke();
        }
        
        // Obtener puntos
        const points = algorithm === 'cubic' ? generateCubicPoints() : generateBBRPoints();
        
        // Cuántos puntos dibujar según animación
        const pointsToDraw = Math.floor(points.length * animationProgress);
        if (pointsToDraw < 2) {
            c.restore();
            return;
        }
        
        const visiblePoints = points.slice(0, pointsToDraw);
        
        // Área bajo la curva (gradient)
        c.beginPath();
        c.moveTo(visiblePoints[0][0], height - padding);
        visiblePoints.forEach(([x, y]) => c.lineTo(x, y));
        c.lineTo(visiblePoints[visiblePoints.length - 1][0], height - padding);
        c.closePath();
        
        const gradient = c.createLinearGradient(0, padding, 0, height - padding);
        gradient.addColorStop(0, bgColor);
        gradient.addColorStop(1, 'transparent');
        c.fillStyle = gradient;
        c.fill();
        
        // Línea principal
        c.beginPath();
        c.moveTo(visiblePoints[0][0], visiblePoints[0][1]);
        visiblePoints.forEach(([x, y]) => c.lineTo(x, y));
        c.strokeStyle = color;
        c.lineWidth = 3;
        c.lineCap = 'round';
        c.lineJoin = 'round';
        c.shadowColor = color;
        c.shadowBlur = 8;
        c.stroke();
        c.shadowBlur = 0;
        
        // Marcadores de pérdida de paquetes
        if (algorithm === 'cubic') {
            // Primera pérdida
            if (animationProgress > 0.27) {
                const lossX = padding + chartWidth * 0.27;
                c.beginPath();
                c.arc(lossX, padding + 8, 6, 0, Math.PI * 2);
                c.fillStyle = 'rgba(255, 68, 68, 0.3)';
                c.fill();
                c.fillStyle = '#ff4444';
                c.font = '10px sans-serif';
                c.textAlign = 'center';
                c.fillText('📉', lossX, padding + 12);
            }
            // Segunda pérdida
            if (animationProgress > 0.57) {
                const lossX = padding + chartWidth * 0.57;
                c.beginPath();
                c.arc(lossX, padding + 8, 6, 0, Math.PI * 2);
                c.fillStyle = 'rgba(255, 68, 68, 0.3)';
                c.fill();
                c.fillStyle = '#ff4444';
                c.font = '10px sans-serif';
                c.textAlign = 'center';
                c.fillText('📉', lossX, padding + 12);
            }
        } else {
            // BBR tolera pérdidas
            if (animationProgress > 0.52) {
                const okX = padding + chartWidth * 0.51;
                c.beginPath();
                c.arc(okX, padding + 8, 6, 0, Math.PI * 2);
                c.fillStyle = 'rgba(0, 212, 170, 0.3)';
                c.fill();
                c.fillStyle = '#00d4aa';
                c.font = '10px sans-serif';
                c.textAlign = 'center';
                c.fillText('✓', okX, padding + 12);
            }
        }
        
        // Labels de ejes
        c.fillStyle = '#666';
        c.font = '9px sans-serif';
        c.textAlign = 'center';
        c.fillText('Tiempo', width / 2, height - 3);
        
        c.save();
        c.translate(8, height / 2);
        c.rotate(-Math.PI / 2);
        c.fillText('Velocidad', 0, 0);
        c.restore();
        
        c.restore();
    }
    
    function startAnimation() {
        if (!animated) {
            animationProgress = 1;
            draw();
            return;
        }
        
        animationProgress = 0;
        
        const animate = () => {
            animationProgress += 0.025;
            draw();
            
            if (animationProgress < 1) {
                animationFrame = requestAnimationFrame(animate);
            } else {
                animationProgress = 1;
                draw();
            }
        };
        
        animationFrame = requestAnimationFrame(animate);
    }
    
    function restart() {
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
        }
        startAnimation();
    }
    
    onMount(() => {
        if (canvasEl) {
            const dpr = window.devicePixelRatio || 1;
            canvasEl.width = width * dpr;
            canvasEl.height = height * dpr;
            ctx = canvasEl.getContext('2d');
            
            // Delay pequeño para asegurar que todo está listo
            setTimeout(() => {
                startAnimation();
            }, 150);
        }
    });
    
    onDestroy(() => {
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
        }
    });
    
    // Re-dibujar cuando cambia el algoritmo
    $: if (ctx && algorithm) {
        restart();
    }
</script>

<div class="chart-container" class:compact on:click={restart} on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && restart()} role="button" tabindex="0" title="Click para reiniciar animación">
    <canvas 
        bind:this={canvasEl}
        style="width: {width}px; height: {height}px;"
    />
    
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
    
    canvas {
        display: block;
        border-radius: 4px;
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
