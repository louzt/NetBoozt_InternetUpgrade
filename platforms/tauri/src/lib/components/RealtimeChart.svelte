<script lang="ts">
    /**
     * NetBoozt - Real-time Chart Component
     * Gráfica en tiempo real con Chart.js
     * 
     * By LOUST (www.loust.pro)
     */
    
    import { onMount, onDestroy } from 'svelte';
    import { Chart } from 'chart.js/auto';
    import 'chartjs-adapter-date-fns';
    import { chartColors, chartTheme, setChartDefaults } from '$lib/charts';
    
    export let title: string = '';
    export let ylabel: string = '';
    export let maxPoints: number = 60;
    export let height: string = '200px';
    
    interface Series {
        name: string;
        color: string;
        data: { x: Date; y: number }[];
    }
    
    let canvas: HTMLCanvasElement;
    let chart: Chart | null = null;
    let seriesMap: Map<string, Series> = new Map();
    
    onMount(() => {
        setChartDefaults(true);
        initChart();
    });
    
    onDestroy(() => {
        if (chart) {
            chart.destroy();
        }
    });
    
    function initChart() {
        if (!canvas) return;
        
        chart = new Chart(canvas, {
            type: 'line',
            data: {
                datasets: []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 10,
                            font: { size: 11 }
                        }
                    },
                    tooltip: {
                        backgroundColor: chartTheme.dark.card,
                        titleColor: chartTheme.dark.text,
                        bodyColor: chartTheme.dark.textSecondary,
                        borderColor: chartTheme.dark.border,
                        borderWidth: 1,
                        padding: 10,
                        displayColors: true,
                        callbacks: {
                            label: (context: any) => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y.toFixed(2);
                                return `${label}: ${value} ${ylabel}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'second',
                            displayFormats: {
                                second: 'HH:mm:ss'
                            }
                        },
                        grid: {
                            color: chartTheme.dark.grid
                        },
                        ticks: {
                            color: chartTheme.dark.textSecondary,
                            maxRotation: 0,
                            font: { size: 10 }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: !!ylabel,
                            text: ylabel,
                            color: chartTheme.dark.textSecondary,
                            font: { size: 11 }
                        },
                        grid: {
                            color: chartTheme.dark.grid
                        },
                        ticks: {
                            color: chartTheme.dark.textSecondary,
                            font: { size: 10 }
                        }
                    }
                },
                animation: {
                    duration: 0
                }
            }
        });
    }
    
    export function addSeries(name: string, color: string, label?: string) {
        if (!chart || seriesMap.has(name)) return;
        
        const series: Series = {
            name,
            color,
            data: []
        };
        
        seriesMap.set(name, series);
        
        chart.data.datasets.push({
            label: label || name,
            data: series.data as any,
            borderColor: color,
            backgroundColor: color.replace(')', ', 0.1)').replace('rgb', 'rgba'),
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2
        });
        
        chart.update('none');
    }
    
    export function addDataPoint(seriesName: string, value: number, timestamp: Date = new Date()) {
        if (!chart) return;
        
        const series = seriesMap.get(seriesName);
        if (!series) return;
        
        const point = { x: timestamp, y: value };
        series.data.push(point);
        
        // Mantener solo los últimos N puntos
        if (series.data.length > maxPoints) {
            series.data.shift();
        }
        
        chart.update('none');
    }
    
    export function update(timestamp: Date, data: Record<string, number>) {
        if (!chart) return;
        
        for (const [name, value] of Object.entries(data)) {
            const series = seriesMap.get(name);
            if (series) {
                series.data.push({ x: timestamp, y: value });
                if (series.data.length > maxPoints) {
                    series.data.shift();
                }
            }
        }
        
        chart.update('none');
    }
    
    export function clear() {
        if (!chart) return;
        
        seriesMap.forEach(series => {
            series.data.length = 0;
        });
        
        chart.update();
    }
</script>

<div class="chart-container" style="--height: {height}">
    {#if title}
        <h3 class="chart-title">{title}</h3>
    {/if}
    <div class="chart-wrapper">
        <canvas bind:this={canvas}></canvas>
    </div>
</div>

<style>
    .chart-container {
        background: var(--bg-card, #2b2b2b);
        border-radius: 12px;
        padding: 1rem;
        height: 100%;
    }
    
    .chart-title {
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        color: var(--text-primary, #fff);
    }
    
    .chart-wrapper {
        height: var(--height);
        position: relative;
    }
</style>
