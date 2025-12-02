<!--
    DiagnosticHistory.svelte - Tabla de historial de diagnósticos mejorada
    Soporta múltiples tipos de diagnóstico, health scores y speed tests
    By LOUST - v2.2
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import Icon from './Icon.svelte';
    import { diagnosticHistory, diagnosticStats, APP_VERSION, type DiagnosticReport, type DiagnosticType, type HealthStatus } from '$lib/stores/diagnosticStore';
    
    export let compact = false;
    export let limit = 5;
    export let filterType: DiagnosticType | 'all' = 'all';
    
    const dispatch = createEventDispatcher();
    
    // Filtrar por tipo si es necesario
    $: filteredReports = filterType === 'all' 
        ? $diagnosticHistory 
        : $diagnosticHistory.filter(r => r.type === filterType);
    $: reports = compact ? filteredReports.slice(0, limit) : filteredReports;
    $: stats = $diagnosticStats as { 
        totalTests?: number; 
        successRate?: number; 
        avgDnsLatency?: number; 
        commonIssue?: string;
        avgHealthScore?: number;
        avgDownloadSpeed?: number;
    };
    
    function formatDate(date: Date): string {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Ahora';
        if (minutes < 60) return `Hace ${minutes}m`;
        if (hours < 24) return `Hace ${hours}h`;
        if (days < 7) return `Hace ${days}d`;
        
        return date.toLocaleDateString('es', { day: 'numeric', month: 'short' });
    }
    
    function formatDuration(ms: number | undefined): string {
        if (!ms) return '-';
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    }
    
    // Iconos y colores para tipos de diagnóstico
    function getTypeInfo(type: DiagnosticType | undefined): { icon: string; label: string; color: string } {
        switch (type) {
            case 'full': return { icon: '🔬', label: 'Completo', color: 'var(--primary, #00d4aa)' };
            case 'quick': return { icon: '⚡', label: 'Rápido', color: 'var(--warning, #fdcb6e)' };
            case 'speedtest': return { icon: '🚀', label: 'Velocidad', color: 'var(--info, #74b9ff)' };
            case 'dns-only': return { icon: '🌐', label: 'DNS', color: 'var(--secondary, #a29bfe)' };
            case 'latency-only': return { icon: '📡', label: 'Latencia', color: 'var(--accent, #fd79a8)' };
            default: return { icon: '📊', label: 'General', color: 'var(--text-muted, #666)' };
        }
    }
    
    // Health status mejorado con score numérico
    function getHealthInfo(health: string, score?: number): { icon: string; label: string; color: string } {
        const baseInfo = {
            'excellent': { icon: '🌟', label: 'Excelente', color: 'var(--primary, #00d4aa)' },
            'good': { icon: '✅', label: 'Bueno', color: 'var(--success, #00b894)' },
            'fair': { icon: '⚠️', label: 'Regular', color: 'var(--warning, #fdcb6e)' },
            'poor': { icon: '🔶', label: 'Pobre', color: 'var(--warning-dark, #e17055)' },
            'critical': { icon: '❌', label: 'Crítico', color: 'var(--error, #ff6b6b)' },
            'warning': { icon: '⚠️', label: 'Advertencia', color: 'var(--warning, #fdcb6e)' },
            'unknown': { icon: '❓', label: 'Desconocido', color: 'var(--text-muted, #666)' }
        };
        
        return baseInfo[health as keyof typeof baseInfo] || baseInfo['unknown'];
    }
    
    function getHealthScoreColor(score: number): string {
        if (score >= 90) return 'var(--primary, #00d4aa)';
        if (score >= 75) return 'var(--success, #00b894)';
        if (score >= 50) return 'var(--warning, #fdcb6e)';
        if (score >= 25) return 'var(--warning-dark, #e17055)';
        return 'var(--error, #ff6b6b)';
    }
    
    function getHealthColor(health: string): string {
        return getHealthInfo(health).color;
    }
    
    function getFailureLabel(point: string): string {
        switch (point) {
            case 'none': return 'Sin fallos';
            case 'adapter': return 'Adaptador';
            case 'router': return 'Router';
            case 'isp': return 'ISP';
            case 'dns': return 'DNS';
            default: return point;
        }
    }
    
    function formatSpeed(mbps: number | undefined): string {
        if (!mbps) return '-';
        if (mbps >= 1000) return `${(mbps / 1000).toFixed(1)} Gbps`;
        return `${mbps.toFixed(1)} Mbps`;
    }
    
    function viewDetails(report: DiagnosticReport) {
        dispatch('viewDetails', report);
    }
    
    function clearAll() {
        if (confirm('¿Eliminar todo el historial de diagnósticos?')) {
            diagnosticHistory.clear();
        }
    }
    
    function exportHistory() {
        const json = diagnosticHistory.export();
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `netboozt-diagnostics-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    function setFilter(type: DiagnosticType | 'all') {
        filterType = type;
        dispatch('filterChange', type);
    }
</script>

<div class="history-container" class:compact>
    {#if !compact}
        <div class="history-header">
            <h3>📊 Historial de Diagnósticos</h3>
            <div class="header-actions">
                <button class="btn-icon" on:click={exportHistory} title="Exportar historial">
                    <Icon name="download" size={16} />
                </button>
                <button class="btn-icon danger" on:click={clearAll} title="Limpiar historial" disabled={$diagnosticHistory.length === 0}>
                    <Icon name="trash-2" size={16} />
                </button>
            </div>
        </div>
        
        <!-- Filtros por tipo -->
        <div class="type-filters">
            <button class="filter-btn" class:active={filterType === 'all'} on:click={() => setFilter('all')}>
                Todos
            </button>
            <button class="filter-btn" class:active={filterType === 'full'} on:click={() => setFilter('full')}>
                🔬 Completo
            </button>
            <button class="filter-btn" class:active={filterType === 'quick'} on:click={() => setFilter('quick')}>
                ⚡ Rápido
            </button>
            <button class="filter-btn" class:active={filterType === 'speedtest'} on:click={() => setFilter('speedtest')}>
                🚀 Velocidad
            </button>
            <button class="filter-btn" class:active={filterType === 'dns-only'} on:click={() => setFilter('dns-only')}>
                🌐 DNS
            </button>
            <button class="filter-btn" class:active={filterType === 'latency-only'} on:click={() => setFilter('latency-only')}>
                📡 Latencia
            </button>
        </div>
        
        <!-- Estadísticas resumen mejoradas -->
        {#if stats && (stats.totalTests ?? 0) > 0}
            <div class="stats-bar">
                <div class="stat">
                    <span class="stat-value">{stats.totalTests}</span>
                    <span class="stat-label">Tests</span>
                </div>
                <div class="stat">
                    <span class="stat-value" style="color: {(stats.successRate ?? 0) >= 80 ? 'var(--primary)' : 'var(--warning)'}">{stats.successRate ?? 0}%</span>
                    <span class="stat-label">Éxito</span>
                </div>
                {#if stats.avgHealthScore !== undefined}
                    <div class="stat">
                        <span class="stat-value" style="color: {getHealthScoreColor(stats.avgHealthScore)}">{stats.avgHealthScore}</span>
                        <span class="stat-label">Score Avg</span>
                    </div>
                {/if}
                <div class="stat">
                    <span class="stat-value">{stats.avgDnsLatency ?? 0}ms</span>
                    <span class="stat-label">DNS Avg</span>
                </div>
                {#if stats.avgDownloadSpeed}
                    <div class="stat">
                        <span class="stat-value" style="color: var(--info)">{formatSpeed(stats.avgDownloadSpeed)}</span>
                        <span class="stat-label">Velocidad Avg</span>
                    </div>
                {/if}
                {#if stats.commonIssue && stats.commonIssue !== 'none'}
                    <div class="stat warning">
                        <span class="stat-value">{getFailureLabel(stats.commonIssue)}</span>
                        <span class="stat-label">Problema común</span>
                    </div>
                {/if}
            </div>
        {/if}
    {/if}
    
    {#if reports.length === 0}
        <div class="empty-state">
            <Icon name="activity" size={24} />
            <p>No hay diagnósticos aún</p>
            <span>Ejecuta un diagnóstico para ver el historial</span>
        </div>
    {:else}
        <div class="history-table">
            <table>
                <thead>
                    <tr>
                        <th>Tipo</th>
                        <th>Estado</th>
                        <th>Score</th>
                        <th>Fecha</th>
                        <th title="Latencias: Router → ISP → DNS">Latencias</th>
                        {#if !compact}
                            <th>Velocidad</th>
                            <th>Duración</th>
                            <th>Fallo</th>
                        {/if}
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {#each reports as report (report.id)}
                        {@const typeInfo = getTypeInfo(report.type)}
                        {@const healthInfo = getHealthInfo(report.health, report.healthScore)}
                        <tr class="report-row" class:issue={report.health !== 'good' && report.health !== 'excellent'}>
                            <!-- Tipo de diagnóstico -->
                            <td class="type-cell">
                                <span class="type-badge" style="--type-color: {typeInfo.color}" title={typeInfo.label}>
                                    {typeInfo.icon}
                                </span>
                            </td>
                            
                            <!-- Estado de salud -->
                            <td class="status-cell">
                                <span class="status-icon" style="color: {healthInfo.color}" title={healthInfo.label}>
                                    {healthInfo.icon}
                                </span>
                            </td>
                            
                            <!-- Health Score -->
                            <td class="score-cell">
                                {#if report.healthScore !== undefined}
                                    <div class="score-badge" style="--score-color: {getHealthScoreColor(report.healthScore)}">
                                        {report.healthScore}
                                    </div>
                                {:else}
                                    <span class="no-score">-</span>
                                {/if}
                            </td>
                            
                            <!-- Fecha -->
                            <td class="date-cell">
                                <span class="date">{formatDate(report.timestamp)}</span>
                            </td>
                            
                            <!-- Latencias (ahora siempre visible) -->
                            <td class="latencies-cell">
                                <div class="latencies-row">
                                    {#if report.routerLatencyMs}
                                        <span class="lat-item" 
                                            class:good={report.routerLatencyMs < 10} 
                                            class:warning={report.routerLatencyMs >= 10 && report.routerLatencyMs < 50} 
                                            class:bad={report.routerLatencyMs >= 50} 
                                            title="Router: {report.routerLatencyMs}ms">
                                            R:{Math.round(report.routerLatencyMs)}
                                        </span>
                                    {/if}
                                    {#if report.ispLatencyMs}
                                        <span class="lat-item" 
                                            class:good={report.ispLatencyMs < 50} 
                                            class:warning={report.ispLatencyMs >= 50 && report.ispLatencyMs < 100} 
                                            class:bad={report.ispLatencyMs >= 100} 
                                            title="ISP: {report.ispLatencyMs}ms">
                                            I:{Math.round(report.ispLatencyMs)}
                                        </span>
                                    {/if}
                                    <span class="lat-item" 
                                        class:good={report.dnsLatencyMs && report.dnsLatencyMs < 50} 
                                        class:warning={report.dnsLatencyMs && report.dnsLatencyMs >= 50 && report.dnsLatencyMs < 150} 
                                        class:bad={report.dnsLatencyMs && report.dnsLatencyMs >= 150} 
                                        title="DNS: {report.dnsLatencyMs || 0}ms">
                                        D:{report.dnsLatencyMs ? Math.round(report.dnsLatencyMs) : '-'}
                                    </span>
                                </div>
                            </td>
                            
                            {#if !compact}
                                <td class="speed-cell">
                                    {#if report.speedTest}
                                        <div class="speed-info">
                                            <span class="download" title="Descarga">↓ {formatSpeed(report.speedTest.downloadMbps)}</span>
                                            {#if report.speedTest.uploadMbps}
                                                <span class="upload" title="Subida">↑ {formatSpeed(report.speedTest.uploadMbps)}</span>
                                            {/if}
                                        </div>
                                    {:else}
                                        <span class="no-speed">-</span>
                                    {/if}
                                </td>
                                
                                <!-- Duración del test -->
                                <td class="duration-cell">
                                    <span class="duration">{formatDuration(report.duration)}</span>
                                </td>
                                
                                <!-- Punto de fallo -->
                                <td class="failure-cell">
                                    <span class="failure" class:none={report.failurePoint === 'none'}>
                                        {getFailureLabel(report.failurePoint)}
                                    </span>
                                </td>
                            {/if}
                            
                            <!-- Acciones -->
                            <td class="actions-cell">
                                <button class="btn-mini" on:click={() => viewDetails(report)} title="Ver detalles">
                                    <Icon name="eye" size={12} />
                                </button>
                            </td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
        
        {#if compact && $diagnosticHistory.length > limit}
            <button class="view-all-btn" on:click={() => dispatch('viewAll')}>
                Ver todos ({$diagnosticHistory.length})
                <Icon name="chevron-right" size={14} />
            </button>
        {/if}
    {/if}
</div>

<style>
    .history-container {
        background: var(--bg-card, #1a1a1a);
        border-radius: 10px;
        padding: 1rem;
    }
    
    .history-container.compact {
        padding: 0.75rem;
    }
    
    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .history-header h3 {
        font-size: 0.9375rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0;
    }
    
    .header-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .btn-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-secondary, #a0a0a0);
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .btn-icon:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .btn-icon.danger:hover:not(:disabled) {
        background: var(--error, #ff6b6b);
        border-color: var(--error, #ff6b6b);
    }
    
    .btn-icon:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    
    /* Filtros por tipo */
    .type-filters {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    
    .filter-btn {
        padding: 0.35rem 0.75rem;
        font-size: 0.6875rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 20px;
        color: var(--text-secondary, #a0a0a0);
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .filter-btn:hover {
        border-color: var(--primary, #00d4aa);
        color: var(--primary, #00d4aa);
    }
    
    .filter-btn.active {
        background: var(--primary, #00d4aa);
        border-color: var(--primary, #00d4aa);
        color: #000;
        font-weight: 600;
    }
    
    .stats-bar {
        display: flex;
        gap: 1rem;
        padding: 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        margin-bottom: 1rem;
        flex-wrap: wrap;
    }
    
    .stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        min-width: 60px;
    }
    
    .stat-value {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
    }
    
    .stat-label {
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
    }
    
    .stat.warning .stat-value {
        color: var(--warning, #fdcb6e);
    }
    
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        color: var(--text-muted, #666);
        text-align: center;
    }
    
    .empty-state p {
        margin: 0.5rem 0 0.25rem 0;
        font-weight: 500;
    }
    
    .empty-state span {
        font-size: 0.75rem;
    }
    
    .history-table {
        overflow-x: auto;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.8125rem;
    }
    
    thead {
        position: sticky;
        top: 0;
        background: var(--bg-card, #1a1a1a);
    }
    
    th {
        text-align: left;
        padding: 0.5rem 0.75rem;
        font-size: 0.6875rem;
        font-weight: 600;
        color: var(--text-muted, #666);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid var(--border, #3d3d3d);
    }
    
    td {
        padding: 0.5rem 0.75rem;
        border-bottom: 1px solid var(--border, #3d3d3d);
        color: var(--text-secondary, #a0a0a0);
    }
    
    .report-row {
        transition: background 0.1s;
    }
    
    .report-row:hover {
        background: var(--bg-elevated, #2b2b2b);
    }
    
    .report-row.issue {
        background: rgba(255, 193, 7, 0.05);
    }
    
    /* Type badge */
    .type-cell {
        width: 40px;
        text-align: center;
    }
    
    .type-badge {
        font-size: 1rem;
        filter: drop-shadow(0 0 3px var(--type-color, transparent));
    }
    
    /* Status cell */
    .status-cell {
        width: 40px;
        text-align: center;
    }
    
    .status-icon {
        font-size: 1rem;
    }
    
    /* Score badge */
    .score-cell {
        width: 50px;
        text-align: center;
    }
    
    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 20px;
        font-size: 0.6875rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        background: rgba(0, 212, 170, 0.15);
        border-radius: 4px;
        color: var(--score-color, var(--primary));
        border: 1px solid var(--score-color, var(--primary));
    }
    
    .no-score {
        color: var(--text-muted, #666);
    }
    
    .date-cell .date {
        font-size: 0.75rem;
    }
    
    /* Latencies cell (all phases) */
    .latencies-cell {
        min-width: 110px;
    }
    
    .latencies-row {
        display: flex;
        gap: 0.35rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
    }
    
    .lat-item {
        padding: 0.1rem 0.3rem;
        border-radius: 3px;
        background: rgba(255,255,255,0.05);
        color: var(--text-muted, #888);
    }
    
    .lat-item.good {
        background: rgba(0, 212, 170, 0.15);
        color: var(--primary, #00d4aa);
    }
    
    .lat-item.warning {
        background: rgba(253, 203, 110, 0.15);
        color: var(--warning, #fdcb6e);
    }
    
    .lat-item.bad {
        background: rgba(255, 107, 107, 0.15);
        color: var(--error, #ff6b6b);
    }
    
    .speed-info {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6875rem;
    }
    
    .speed-info .download {
        color: var(--primary, #00d4aa);
    }
    
    .speed-info .upload {
        color: var(--info, #74b9ff);
    }
    
    .no-speed {
        color: var(--text-muted, #666);
        font-size: 0.75rem;
    }
    
    /* Duration cell */
    .duration-cell .duration {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
    }
    
    .failure {
        font-size: 0.6875rem;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        background: rgba(255, 107, 107, 0.15);
        color: var(--error, #ff6b6b);
    }
    
    .failure.none {
        background: rgba(0, 212, 170, 0.15);
        color: var(--primary, #00d4aa);
    }
    
    .actions-cell {
        width: 40px;
    }
    
    .btn-mini {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.1s;
    }
    
    .btn-mini:hover {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    .view-all-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
        width: 100%;
        padding: 0.5rem;
        margin-top: 0.5rem;
        background: transparent;
        border: 1px dashed var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .view-all-btn:hover {
        border-color: var(--primary, #00d4aa);
        color: var(--primary, #00d4aa);
    }
    
    .compact table {
        font-size: 0.75rem;
    }
    
    .compact th, .compact td {
        padding: 0.35rem 0.5rem;
    }
    
    /* Responsive */
    @media (max-width: 600px) {
        .type-filters {
            gap: 0.35rem;
        }
        
        .filter-btn {
            padding: 0.25rem 0.5rem;
            font-size: 0.625rem;
        }
        
        .stats-bar {
            gap: 0.5rem;
        }
        
        .stat-value {
            font-size: 0.875rem;
        }
    }
</style>
