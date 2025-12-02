/**
 * NetBoozt - Chart Utilities
 * Utilidades para gráficas con Chart.js
 * 
 * By LOUST (www.loust.pro)
 */

import { Chart, registerables } from 'chart.js';

// Registrar todos los componentes de Chart.js
Chart.register(...registerables);

// ============================================
// Theme Colors
// ============================================

export const chartColors = {
    primary: '#00d4aa',
    secondary: '#6c5ce7',
    warning: '#fdcb6e',
    error: '#ff6b6b',
    info: '#00a8ff',
    success: '#00ff88',
    purple: '#a55eea',
    cyan: '#00d2d3',
    pink: '#ff9ff3',
    
    // Con transparencia
    primaryAlpha: 'rgba(0, 212, 170, 0.2)',
    secondaryAlpha: 'rgba(108, 92, 231, 0.2)',
    warningAlpha: 'rgba(253, 203, 110, 0.2)',
    errorAlpha: 'rgba(255, 107, 107, 0.2)',
};

export const chartTheme = {
    dark: {
        background: '#1a1a1a',
        card: '#2b2b2b',
        text: '#ffffff',
        textSecondary: '#a0a0a0',
        grid: 'rgba(255, 255, 255, 0.1)',
        border: '#3d3d3d'
    },
    light: {
        background: '#ffffff',
        card: '#f5f5f5',
        text: '#1a1a1a',
        textSecondary: '#666666',
        grid: 'rgba(0, 0, 0, 0.1)',
        border: '#e0e0e0'
    }
};

// ============================================
// Chart Defaults
// ============================================

export function setChartDefaults(isDark: boolean = true) {
    const theme = isDark ? chartTheme.dark : chartTheme.light;
    
    Chart.defaults.color = theme.textSecondary;
    Chart.defaults.borderColor = theme.border;
    Chart.defaults.backgroundColor = theme.background;
    
    // Fonts
    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 12;
    
    // Scales
    Chart.defaults.scale.grid.color = theme.grid;
    Chart.defaults.scale.ticks.color = theme.textSecondary;
    
    // Plugins
    Chart.defaults.plugins.legend.labels.color = theme.text;
    Chart.defaults.plugins.tooltip.backgroundColor = theme.card;
    Chart.defaults.plugins.tooltip.titleColor = theme.text;
    Chart.defaults.plugins.tooltip.bodyColor = theme.textSecondary;
    Chart.defaults.plugins.tooltip.borderColor = theme.border;
    Chart.defaults.plugins.tooltip.borderWidth = 1;
}

// ============================================
// Chart Configurations
// ============================================

export interface TimeSeriesDataPoint {
    x: Date | number;
    y: number;
}

/**
 * Configuración para gráfica de velocidad de red
 */
export function createSpeedChartConfig(downloadData: TimeSeriesDataPoint[], uploadData: TimeSeriesDataPoint[]) {
    return {
        type: 'line' as const,
        data: {
            datasets: [
                {
                    label: 'Descarga',
                    data: downloadData,
                    borderColor: chartColors.info,
                    backgroundColor: 'rgba(0, 168, 255, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2
                },
                {
                    label: 'Subida',
                    data: uploadData,
                    borderColor: chartColors.success,
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index' as const
            },
            plugins: {
                legend: {
                    position: 'top' as const,
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context: any) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)} Mbps`
                    }
                }
            },
            scales: {
                x: {
                    type: 'time' as const,
                    time: {
                        unit: 'second' as const,
                        displayFormats: {
                            second: 'HH:mm:ss'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Tiempo'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Mbps'
                    }
                }
            },
            animation: {
                duration: 0
            }
        }
    };
}

/**
 * Configuración para gráfica de latencia
 */
export function createLatencyChartConfig(data: TimeSeriesDataPoint[]) {
    return {
        type: 'line' as const,
        data: {
            datasets: [{
                label: 'Latencia',
                data: data,
                borderColor: chartColors.warning,
                backgroundColor: chartColors.warningAlpha,
                fill: true,
                tension: 0.3,
                pointRadius: 0,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: (context: any) => `${context.parsed.y.toFixed(1)} ms`
                    }
                }
            },
            scales: {
                x: {
                    type: 'time' as const,
                    time: {
                        unit: 'second' as const,
                        displayFormats: {
                            second: 'HH:mm:ss'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'ms'
                    }
                }
            },
            animation: {
                duration: 0
            }
        }
    };
}

/**
 * Configuración para gráfica de paquetes
 */
export function createPacketsChartConfig(sentData: TimeSeriesDataPoint[], recvData: TimeSeriesDataPoint[]) {
    return {
        type: 'line' as const,
        data: {
            datasets: [
                {
                    label: 'Enviados',
                    data: sentData,
                    borderColor: chartColors.purple,
                    backgroundColor: 'rgba(165, 94, 234, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2
                },
                {
                    label: 'Recibidos',
                    data: recvData,
                    borderColor: chartColors.cyan,
                    backgroundColor: 'rgba(0, 210, 211, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top' as const,
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context: any) => `${context.dataset.label}: ${context.parsed.y.toFixed(0)}/s`
                    }
                }
            },
            scales: {
                x: {
                    type: 'time' as const,
                    time: {
                        unit: 'second' as const,
                        displayFormats: {
                            second: 'HH:mm:ss'
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'paquetes/s'
                    }
                }
            },
            animation: {
                duration: 0
            }
        }
    };
}

/**
 * Configuración para gráfica de errores
 */
export function createErrorsChartConfig(errorsData: TimeSeriesDataPoint[], dropsData: TimeSeriesDataPoint[]) {
    return {
        type: 'bar' as const,
        data: {
            datasets: [
                {
                    label: 'Errores',
                    data: errorsData,
                    backgroundColor: chartColors.error,
                    borderColor: chartColors.error,
                    borderWidth: 1
                },
                {
                    label: 'Drops',
                    data: dropsData,
                    backgroundColor: chartColors.pink,
                    borderColor: chartColors.pink,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top' as const,
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                }
            },
            scales: {
                x: {
                    type: 'time' as const,
                    time: {
                        unit: 'second' as const,
                        displayFormats: {
                            second: 'HH:mm:ss'
                        }
                    },
                    stacked: true
                },
                y: {
                    beginAtZero: true,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'count'
                    }
                }
            },
            animation: {
                duration: 0
            }
        }
    };
}

/**
 * Configuración para gauge de salud
 */
export function createHealthGaugeConfig(value: number, label: string) {
    return {
        type: 'doughnut' as const,
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [
                    value >= 80 ? chartColors.success :
                    value >= 60 ? chartColors.primary :
                    value >= 40 ? chartColors.warning :
                    chartColors.error,
                    'rgba(255, 255, 255, 0.1)'
                ],
                borderWidth: 0,
                circumference: 180,
                rotation: 270
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    };
}

/**
 * Configuración para gráfica de speed test
 */
export function createSpeedTestChartConfig(results: { timestamp: string; download: number; upload: number }[]) {
    return {
        type: 'bar' as const,
        data: {
            labels: results.map(r => new Date(r.timestamp).toLocaleDateString()),
            datasets: [
                {
                    label: 'Descarga',
                    data: results.map(r => r.download),
                    backgroundColor: chartColors.info,
                    borderRadius: 4
                },
                {
                    label: 'Subida',
                    data: results.map(r => r.upload),
                    backgroundColor: chartColors.success,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top' as const
                },
                tooltip: {
                    callbacks: {
                        label: (context: any) => `${context.dataset.label}: ${context.parsed.y.toFixed(2)} Mbps`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Mbps'
                    }
                }
            }
        }
    };
}

// ============================================
// Helper Functions
// ============================================

/**
 * Agregar punto de datos a un dataset existente
 */
export function addDataPoint(chart: Chart, datasetIndex: number, point: TimeSeriesDataPoint, maxPoints: number = 60) {
    const dataset = chart.data.datasets[datasetIndex];
    if (!dataset) return;
    
    (dataset.data as TimeSeriesDataPoint[]).push(point);
    
    // Mantener solo los últimos N puntos
    if (dataset.data.length > maxPoints) {
        (dataset.data as TimeSeriesDataPoint[]).shift();
    }
    
    chart.update('none'); // Update sin animación
}

/**
 * Limpiar datos de un chart
 */
export function clearChartData(chart: Chart) {
    chart.data.datasets.forEach((dataset: any) => {
        dataset.data = [];
    });
    chart.update();
}

/**
 * Actualizar colores del chart según tema
 */
export function updateChartTheme(chart: Chart, isDark: boolean) {
    const theme = isDark ? chartTheme.dark : chartTheme.light;
    
    if (chart.options.scales) {
        Object.values(chart.options.scales).forEach((scale: any) => {
            if (scale.grid) {
                scale.grid.color = theme.grid;
            }
            if (scale.ticks) {
                scale.ticks.color = theme.textSecondary;
            }
        });
    }
    
    if (chart.options.plugins?.legend?.labels) {
        chart.options.plugins.legend.labels.color = theme.text;
    }
    
    chart.update();
}

// Inicializar defaults al cargar
setChartDefaults(true);
