/**
 * Diagnostic Store - Historial de diagnósticos de red
 * Almacena los últimos 20 diagnósticos con persistencia local
 * Incluye: diagnósticos de red, speed tests, health checks
 * By LOUST
 */
import { writable, derived, get } from 'svelte/store';
import { browser } from '$app/environment';

// Tipo de diagnóstico
export type DiagnosticType = 'full' | 'quick' | 'speedtest' | 'dns-only' | 'latency-only';

// Estado de salud mejorado (incluye 'warning' para compatibilidad)
export type HealthStatus = 'excellent' | 'good' | 'fair' | 'poor' | 'critical' | 'warning' | 'unknown';

export interface DiagnosticReport {
    id: string;
    timestamp: Date;
    appVersion: string;
    type: DiagnosticType;
    
    // Resultados generales
    health: HealthStatus;
    healthScore: number; // 0-100
    failurePoint: 'none' | 'adapter' | 'router' | 'isp' | 'dns' | 'speed';
    
    // Fases de conectividad
    adapterOk: boolean;
    adapterName: string;
    routerOk: boolean;
    routerLatencyMs: number;
    ispOk: boolean;
    ispLatencyMs: number;
    dnsOk: boolean;
    dnsLatencyMs: number;
    
    // Speed Test (opcional)
    speedTest?: {
        downloadMbps: number;
        uploadMbps: number;
        pingMs: number;
        jitterMs: number;
        serverName: string;
    };
    
    // Métricas de tráfico en vivo (opcional)
    liveMetrics?: {
        downloadMbps: number;
        uploadMbps: number;
        latencyMs: number;
    };
    
    // Metadata
    recommendation: string;
    selectedAdapter?: string;
    dnsServers?: string[];
    duration?: number; // Duración del test en segundos
}

// Máximo de diagnósticos a guardar
const MAX_HISTORY = 20;

// Versión de la app
export const APP_VERSION = '3.0.0-beta';

// Helper para calcular score de salud
export function calculateHealthScore(report: Partial<DiagnosticReport>): { score: number; status: HealthStatus } {
    let score = 100;
    
    // Penalizaciones por latencia
    if (report.dnsLatencyMs) {
        if (report.dnsLatencyMs > 500) score -= 30;
        else if (report.dnsLatencyMs > 200) score -= 15;
        else if (report.dnsLatencyMs > 100) score -= 5;
    }
    
    if (report.routerLatencyMs) {
        if (report.routerLatencyMs > 100) score -= 20;
        else if (report.routerLatencyMs > 50) score -= 10;
        else if (report.routerLatencyMs > 20) score -= 5;
    }
    
    // Penalizaciones por velocidad
    if (report.speedTest) {
        if (report.speedTest.downloadMbps < 5) score -= 30;
        else if (report.speedTest.downloadMbps < 10) score -= 20;
        else if (report.speedTest.downloadMbps < 25) score -= 10;
        
        if (report.speedTest.uploadMbps < 1) score -= 15;
        else if (report.speedTest.uploadMbps < 5) score -= 10;
        
        if (report.speedTest.jitterMs > 50) score -= 15;
        else if (report.speedTest.jitterMs > 20) score -= 5;
    }
    
    // Penalizaciones por fallos
    if (!report.adapterOk) score -= 50;
    if (!report.routerOk) score -= 40;
    if (!report.ispOk) score -= 30;
    if (!report.dnsOk) score -= 20;
    
    score = Math.max(0, Math.min(100, score));
    
    let status: HealthStatus;
    if (score >= 90) status = 'excellent';
    else if (score >= 75) status = 'good';
    else if (score >= 50) status = 'fair';
    else if (score >= 25) status = 'poor';
    else status = 'critical';
    
    return { score, status };
}

// Store principal
const createDiagnosticStore = () => {
    // Intentar cargar del localStorage
    let initial: DiagnosticReport[] = [];
    if (browser) {
        try {
            const saved = localStorage.getItem('netboozt_diagnostics');
            if (saved) {
                initial = JSON.parse(saved).map((d: any) => ({
                    ...d,
                    timestamp: new Date(d.timestamp)
                }));
            }
        } catch (e) {
            console.warn('Error loading diagnostic history:', e);
        }
    }
    
    const { subscribe, set, update } = writable<DiagnosticReport[]>(initial);
    
    // Guardar en localStorage cuando cambie
    if (browser) {
        subscribe((reports) => {
            try {
                localStorage.setItem('netboozt_diagnostics', JSON.stringify(reports));
            } catch (e) {
                console.warn('Error saving diagnostic history:', e);
            }
        });
    }
    
    return {
        subscribe,
        
        /**
         * Agregar un nuevo diagnóstico
         */
        add(result: Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'>) {
            const report: DiagnosticReport = {
                ...result,
                id: `diag-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                timestamp: new Date(),
                appVersion: APP_VERSION,
            };
            
            update((reports) => {
                const updated = [report, ...reports];
                // Limitar a MAX_HISTORY
                return updated.slice(0, MAX_HISTORY);
            });
            
            return report.id;
        },
        
        /**
         * Obtener diagnóstico por ID
         */
        getById(id: string): DiagnosticReport | undefined {
            const reports = get({ subscribe });
            return reports.find(r => r.id === id);
        },
        
        /**
         * Eliminar un diagnóstico
         */
        remove(id: string) {
            update((reports) => reports.filter(r => r.id !== id));
        },
        
        /**
         * Limpiar todo el historial
         */
        clear() {
            set([]);
        },
        
        /**
         * Obtener el último diagnóstico
         */
        getLatest(): DiagnosticReport | undefined {
            const reports = get({ subscribe });
            return reports[0];
        },
        
        /**
         * Exportar historial como JSON
         */
        export(): string {
            const reports = get({ subscribe });
            return JSON.stringify({
                exportDate: new Date().toISOString(),
                appVersion: APP_VERSION,
                reports
            }, null, 2);
        },
        
        /**
         * Importar historial desde JSON
         */
        import(jsonString: string) {
            try {
                const data = JSON.parse(jsonString);
                if (data.reports && Array.isArray(data.reports)) {
                    const imported = data.reports.map((d: any) => ({
                        ...d,
                        timestamp: new Date(d.timestamp)
                    }));
                    set(imported.slice(0, MAX_HISTORY));
                    return true;
                }
                return false;
            } catch (e) {
                console.error('Error importing diagnostics:', e);
                return false;
            }
        }
    };
};

export const diagnosticHistory = createDiagnosticStore();

// Derivados útiles
export const latestDiagnostic = derived(diagnosticHistory, ($history) => $history[0]);
export const diagnosticCount = derived(diagnosticHistory, ($history) => $history.length);
export const hasIssues = derived(diagnosticHistory, ($history) => {
    const latest = $history[0];
    return latest && latest.health !== 'good';
});

// Estadísticas mejoradas
export const diagnosticStats = derived(diagnosticHistory, ($history) => {
    if ($history.length === 0) {
        return { 
            avgDnsLatency: 0, 
            avgRouterLatency: 0,
            successRate: 0, 
            commonIssue: 'none',
            totalTests: 0,
            avgHealthScore: 0,
            avgDownloadSpeed: 0,
            avgUploadSpeed: 0,
            testsByType: {} as Record<DiagnosticType, number>
        };
    }
    
    const avgDnsLatency = $history.reduce((sum, d) => sum + (d.dnsLatencyMs || 0), 0) / $history.length;
    const avgRouterLatency = $history.reduce((sum, d) => sum + (d.routerLatencyMs || 0), 0) / $history.length;
    
    // Health scores (solo los que tienen score)
    const withScore = $history.filter(d => d.healthScore !== undefined);
    const avgHealthScore = withScore.length > 0 
        ? Math.round(withScore.reduce((sum, d) => sum + (d.healthScore || 0), 0) / withScore.length)
        : 0;
    
    // Speed tests
    const withSpeed = $history.filter(d => d.speedTest);
    const avgDownloadSpeed = withSpeed.length > 0
        ? Math.round(withSpeed.reduce((sum, d) => sum + (d.speedTest?.downloadMbps || 0), 0) / withSpeed.length * 10) / 10
        : 0;
    const avgUploadSpeed = withSpeed.length > 0
        ? Math.round(withSpeed.reduce((sum, d) => sum + (d.speedTest?.uploadMbps || 0), 0) / withSpeed.length * 10) / 10
        : 0;
    
    // Success rate (good + excellent)
    const successCount = $history.filter(d => d.health === 'good' || d.health === 'excellent').length;
    
    // Conteo por tipo
    const testsByType = $history.reduce((acc, d) => {
        const type = d.type || 'full';
        acc[type] = (acc[type] || 0) + 1;
        return acc;
    }, {} as Record<DiagnosticType, number>);
    
    // Encontrar problema más común
    const issues = $history
        .filter(d => d.failurePoint !== 'none')
        .map(d => d.failurePoint);
    const issueCounts = issues.reduce((acc, issue) => {
        acc[issue] = (acc[issue] || 0) + 1;
        return acc;
    }, {} as Record<string, number>);
    
    const commonIssue = Object.entries(issueCounts)
        .sort((a, b) => b[1] - a[1])[0]?.[0] || 'none';
    
    return {
        avgDnsLatency: Math.round(avgDnsLatency),
        avgRouterLatency: Math.round(avgRouterLatency),
        successRate: Math.round((successCount / $history.length) * 100),
        commonIssue,
        totalTests: $history.length,
        avgHealthScore,
        avgDownloadSpeed,
        avgUploadSpeed,
        testsByType
    };
});

// Helpers para crear diagnósticos de diferentes tipos
export function createSpeedTestReport(speedResult: {
    downloadMbps: number;
    uploadMbps: number;
    pingMs: number;
    jitterMs: number;
    serverName: string;
}): Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'> {
    const partial: Partial<DiagnosticReport> = {
        type: 'speedtest',
        speedTest: speedResult,
        adapterOk: true,
        routerOk: true,
        ispOk: true,
        dnsOk: true,
        adapterName: '',
        routerLatencyMs: 0,
        ispLatencyMs: 0,
        dnsLatencyMs: speedResult.pingMs,
        failurePoint: 'none',
        recommendation: getSpeedRecommendation(speedResult.downloadMbps)
    };
    
    const { score, status } = calculateHealthScore(partial);
    
    return {
        ...partial,
        health: status,
        healthScore: score
    } as Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'>;
}

export function createDnsOnlyReport(dnsResult: {
    latencyMs: number;
    isOk: boolean;
    servers: string[];
}): Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'> {
    const partial: Partial<DiagnosticReport> = {
        type: 'dns-only',
        dnsOk: dnsResult.isOk,
        dnsLatencyMs: dnsResult.latencyMs,
        dnsServers: dnsResult.servers,
        adapterOk: true,
        routerOk: true,
        ispOk: true,
        adapterName: '',
        routerLatencyMs: 0,
        ispLatencyMs: 0,
        failurePoint: dnsResult.isOk ? 'none' : 'dns',
        recommendation: getDnsRecommendation(dnsResult.latencyMs, dnsResult.isOk)
    };
    
    const { score, status } = calculateHealthScore(partial);
    
    return {
        ...partial,
        health: status,
        healthScore: score
    } as Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'>;
}

export function createLatencyOnlyReport(latencyResult: {
    routerMs: number;
    ispMs: number;
    dnsMs: number;
}): Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'> {
    const partial: Partial<DiagnosticReport> = {
        type: 'latency-only',
        routerLatencyMs: latencyResult.routerMs,
        ispLatencyMs: latencyResult.ispMs,
        dnsLatencyMs: latencyResult.dnsMs,
        adapterOk: true,
        routerOk: latencyResult.routerMs < 100,
        ispOk: latencyResult.ispMs < 150,
        dnsOk: latencyResult.dnsMs < 200,
        adapterName: '',
        failurePoint: 'none',
        recommendation: getLatencyRecommendation(latencyResult)
    };
    
    const { score, status } = calculateHealthScore(partial);
    
    return {
        ...partial,
        health: status,
        healthScore: score
    } as Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'>;
}

// Helpers para recomendaciones
function getSpeedRecommendation(downloadMbps: number): string {
    if (downloadMbps >= 100) return 'Excelente velocidad. Tu conexión es óptima para cualquier uso.';
    if (downloadMbps >= 50) return 'Muy buena velocidad. Ideal para streaming 4K y gaming.';
    if (downloadMbps >= 25) return 'Buena velocidad. Suficiente para la mayoría de actividades.';
    if (downloadMbps >= 10) return 'Velocidad aceptable. Puede haber limitaciones con múltiples dispositivos.';
    return 'Velocidad baja. Considera optimizar tu conexión o contactar a tu ISP.';
}

function getDnsRecommendation(latencyMs: number, isOk: boolean): string {
    if (!isOk) return 'DNS no responde. Prueba cambiar a DNS alternativos (1.1.1.1, 8.8.8.8).';
    if (latencyMs < 20) return 'DNS ultra-rápido. Sin mejoras necesarias.';
    if (latencyMs < 50) return 'DNS rápido. Rendimiento óptimo.';
    if (latencyMs < 100) return 'DNS aceptable. Podrías mejorar con DNS más cercano.';
    return 'DNS lento. Se recomienda cambiar a un servidor DNS más rápido.';
}

function getLatencyRecommendation(latency: { routerMs: number; ispMs: number; dnsMs: number }): string {
    if (latency.routerMs > 100) return 'Alta latencia al router. Verifica tu conexión WiFi o usa cable Ethernet.';
    if (latency.ispMs > 150) return 'Alta latencia al ISP. Puede haber congestión en la red.';
    if (latency.dnsMs > 200) return 'Alta latencia DNS. Considera cambiar servidor DNS.';
    if (latency.routerMs < 5 && latency.ispMs < 30 && latency.dnsMs < 30) {
        return 'Latencia excelente en todas las fases. Red optimizada.';
    }
    return 'Latencia general aceptable. Sin problemas significativos detectados.';
}
