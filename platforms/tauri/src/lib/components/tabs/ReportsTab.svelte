<!--
    ReportsTab.svelte - Tab de reportes e historial de diagnósticos
    Vista completa con filtros por tipo, speed tests y health scores
    By LOUST v2.2
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import Icon from '../Icon.svelte';
    import DiagnosticHistory from '../DiagnosticHistory.svelte';
    import { diagnosticHistory, diagnosticStats, type DiagnosticReport, type DiagnosticType } from '$lib/stores/diagnosticStore';
    
    const dispatch = createEventDispatcher();
    
    let selectedReport: DiagnosticReport | null = null;
    let showImportModal = false;
    let importJson = '';
    let importError = '';
    let currentFilter: DiagnosticType | 'all' = 'all';
    
    $: stats = $diagnosticStats;
    
    function handleViewDetails(event: CustomEvent<DiagnosticReport>) {
        selectedReport = event.detail;
    }
    
    function handleFilterChange(event: CustomEvent<DiagnosticType | 'all'>) {
        currentFilter = event.detail;
    }
    
    function closeDetails() {
        selectedReport = null;
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
    
    function openImportModal() {
        importJson = '';
        importError = '';
        showImportModal = true;
    }
    
    function closeImportModal() {
        showImportModal = false;
    }
    
    function handleImport() {
        importError = '';
        if (!importJson.trim()) {
            importError = 'Por favor pega el JSON a importar';
            return;
        }
        
        const success = diagnosticHistory.import(importJson);
        if (success) {
            showImportModal = false;
        } else {
            importError = 'El JSON no es válido o no contiene diagnósticos';
        }
    }
    
    function formatFullDate(date: Date): string {
        return date.toLocaleString('es', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    function formatDuration(ms: number | undefined): string {
        if (!ms) return '-';
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    }
    
    function formatSpeed(mbps: number | undefined): string {
        if (!mbps) return '-';
        if (mbps >= 1000) return `${(mbps / 1000).toFixed(1)} Gbps`;
        return `${mbps.toFixed(1)} Mbps`;
    }
    
    function getHealthLabel(health: string, score?: number): string {
        const labels: Record<string, string> = {
            'excellent': '🌟 Excelente',
            'good': '✅ Bueno',
            'fair': '⚠️ Regular',
            'poor': '🔶 Pobre',
            'critical': '❌ Crítico',
            'warning': '⚠️ Advertencia',
            'unknown': '❓ Desconocido'
        };
        const label = labels[health] || labels['unknown'];
        return score !== undefined ? `${label} (${score}/100)` : label;
    }
    
    function getTypeLabel(type: DiagnosticType | string | undefined): { icon: string; label: string } {
        const types: Record<string, { icon: string; label: string }> = {
            'full': { icon: '🔬', label: 'Diagnóstico Completo' },
            'quick': { icon: '⚡', label: 'Diagnóstico Rápido' },
            'speedtest': { icon: '🚀', label: 'Test de Velocidad' },
            'dns-only': { icon: '🌐', label: 'Test DNS' },
            'latency-only': { icon: '📡', label: 'Test de Latencia' }
        };
        return types[type || 'full'] || types['full'];
    }
    
    function getFailurePointLabel(point: string): string {
        switch (point) {
            case 'none': return '✅ Ninguno';
            case 'adapter': return '🔌 Adaptador de red';
            case 'router': return '📡 Router/Gateway';
            case 'isp': return '🌐 ISP/Internet';
            case 'dns': return '🌍 DNS';
            case 'speed': return '🚀 Velocidad';
            default: return point;
        }
    }
    
    function getHealthScoreColor(score: number): string {
        if (score >= 90) return 'var(--primary, #00d4aa)';
        if (score >= 75) return 'var(--success, #00b894)';
        if (score >= 50) return 'var(--warning, #fdcb6e)';
        if (score >= 25) return 'var(--warning-dark, #e17055)';
        return 'var(--error, #ff6b6b)';
    }
</script>

<div class="reports-tab">
    <!-- Actions Bar -->
    <div class="actions-bar">
        <button class="btn btn-secondary" on:click={openImportModal}>
            <Icon name="upload" size={16} />
            Importar
        </button>
        <button class="btn btn-secondary" on:click={exportHistory} disabled={$diagnosticHistory.length === 0}>
            <Icon name="download" size={16} />
            Exportar
        </button>
    </div>
    
    <!-- Estadísticas Generales Mejoradas -->
    {#if stats && (stats.totalTests ?? 0) > 0}
        <section class="stats-overview">
            <div class="stat-card">
                <Icon name="clipboard-list" size={24} />
                <div class="stat-content">
                    <span class="stat-value">{stats.totalTests}</span>
                    <span class="stat-label">Tests Totales</span>
                </div>
            </div>
            <div class="stat-card">
                <Icon name="check-circle" size={24} />
                <div class="stat-content">
                    <span class="stat-value success">{stats.successRate ?? 0}%</span>
                    <span class="stat-label">Tasa de Éxito</span>
                </div>
            </div>
            {#if stats.avgHealthScore > 0}
                <div class="stat-card">
                    <Icon name="heart" size={24} />
                    <div class="stat-content">
                        <span class="stat-value" style="color: {getHealthScoreColor(stats.avgHealthScore)}">{stats.avgHealthScore}</span>
                        <span class="stat-label">Health Score Avg</span>
                    </div>
                </div>
            {/if}
            <div class="stat-card">
                <Icon name="zap" size={24} />
                <div class="stat-content">
                    <span class="stat-value">{stats.avgDnsLatency ?? 0}ms</span>
                    <span class="stat-label">DNS Promedio</span>
                </div>
            </div>
            {#if stats.avgDownloadSpeed > 0}
                <div class="stat-card">
                    <Icon name="download" size={24} />
                    <div class="stat-content">
                        <span class="stat-value" style="color: var(--info, #74b9ff)">{formatSpeed(stats.avgDownloadSpeed)}</span>
                        <span class="stat-label">Descarga Avg</span>
                    </div>
                </div>
            {/if}
            {#if stats.avgUploadSpeed > 0}
                <div class="stat-card">
                    <Icon name="upload" size={24} />
                    <div class="stat-content">
                        <span class="stat-value" style="color: var(--secondary, #a29bfe)">{formatSpeed(stats.avgUploadSpeed)}</span>
                        <span class="stat-label">Subida Avg</span>
                    </div>
                </div>
            {/if}
            {#if stats.commonIssue && stats.commonIssue !== 'none'}
                <div class="stat-card warning">
                    <Icon name="alert-triangle" size={24} />
                    <div class="stat-content">
                        <span class="stat-value">{getFailurePointLabel(stats.commonIssue)}</span>
                        <span class="stat-label">Problema Frecuente</span>
                    </div>
                </div>
            {/if}
        </section>
        
        <!-- Conteo por tipo de test -->
        {#if stats.testsByType && Object.keys(stats.testsByType).length > 0}
            <section class="tests-by-type">
                <h3>Tests por Tipo</h3>
                <div class="type-badges">
                    {#each Object.entries(stats.testsByType) as [type, count]}
                        {@const typeInfo = getTypeLabel(type)}
                        <div class="type-badge">
                            <span class="type-icon">{typeInfo.icon}</span>
                            <span class="type-count">{count}</span>
                            <span class="type-name">{typeInfo.label}</span>
                        </div>
                    {/each}
                </div>
            </section>
        {/if}
    {/if}
    
    <!-- Historial Completo -->
    <section class="history-section">
        <DiagnosticHistory 
            compact={false}
            filterType={currentFilter}
            on:viewDetails={handleViewDetails}
            on:filterChange={handleFilterChange}
        />
    </section>
</div>

<!-- Modal de Detalles Mejorado -->
{#if selectedReport}
    {@const typeInfo = getTypeLabel(selectedReport.type)}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
    <div class="modal-overlay" on:click={closeDetails} role="dialog" aria-modal="true">
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
        <div class="modal" on:click|stopPropagation role="document">
            <header class="modal-header">
                <div class="modal-title">
                    <span class="type-icon-large">{typeInfo.icon}</span>
                    <div>
                        <h2>{typeInfo.label}</h2>
                        <span class="modal-date">{formatFullDate(selectedReport.timestamp)}</span>
                    </div>
                </div>
                <button class="close-btn" on:click={closeDetails}>
                    <Icon name="x" size={20} />
                </button>
            </header>
            
            <div class="modal-content">
                <!-- Health Score Badge -->
                {#if selectedReport.healthScore !== undefined}
                    <div class="health-score-section">
                        <div class="health-score-badge" style="--score-color: {getHealthScoreColor(selectedReport.healthScore)}">
                            <span class="score-value">{selectedReport.healthScore}</span>
                            <span class="score-max">/100</span>
                        </div>
                        <div class="health-info">
                            <span class="health-status">{getHealthLabel(selectedReport.health)}</span>
                            {#if selectedReport.duration}
                                <span class="test-duration">Duración: {formatDuration(selectedReport.duration)}</span>
                            {/if}
                        </div>
                    </div>
                {/if}
                
                <!-- Speed Test Results -->
                {#if selectedReport.speedTest}
                    <div class="detail-section">
                        <h3>🚀 Resultados de Velocidad</h3>
                        <div class="speed-results">
                            <div class="speed-box download">
                                <span class="speed-label">Descarga</span>
                                <span class="speed-value">{formatSpeed(selectedReport.speedTest.downloadMbps)}</span>
                            </div>
                            <div class="speed-box upload">
                                <span class="speed-label">Subida</span>
                                <span class="speed-value">{formatSpeed(selectedReport.speedTest.uploadMbps)}</span>
                            </div>
                            <div class="speed-box ping">
                                <span class="speed-label">Ping</span>
                                <span class="speed-value">{selectedReport.speedTest.pingMs.toFixed(0)}ms</span>
                            </div>
                            <div class="speed-box jitter">
                                <span class="speed-label">Jitter</span>
                                <span class="speed-value">{selectedReport.speedTest.jitterMs.toFixed(1)}ms</span>
                            </div>
                        </div>
                        {#if selectedReport.speedTest.serverName}
                            <span class="server-name">Servidor: {selectedReport.speedTest.serverName}</span>
                        {/if}
                    </div>
                {/if}
                
                <!-- Información General -->
                <div class="detail-section">
                    <h3>📋 Información General</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="label">Versión App:</span>
                            <span class="value">{selectedReport.appVersion}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Punto de Falla:</span>
                            <span class="value">{getFailurePointLabel(selectedReport.failurePoint)}</span>
                        </div>
                        {#if selectedReport.selectedAdapter}
                            <div class="detail-item">
                                <span class="label">Adaptador:</span>
                                <span class="value">{selectedReport.selectedAdapter}</span>
                            </div>
                        {/if}
                    </div>
                </div>
                
                <!-- Fases del Diagnóstico -->
                {#if selectedReport.type !== 'speedtest'}
                    <div class="detail-section">
                        <h3>🔍 Fases del Diagnóstico</h3>
                        <div class="phases-grid">
                            <div class="phase" class:success={selectedReport.adapterOk} class:failed={!selectedReport.adapterOk}>
                                <span class="phase-icon">{selectedReport.adapterOk ? '✅' : '❌'}</span>
                                <span class="phase-name">Adaptador</span>
                                <span class="phase-detail">{selectedReport.adapterName || 'N/A'}</span>
                            </div>
                            <div class="phase" class:success={selectedReport.routerOk} class:failed={!selectedReport.routerOk}>
                                <span class="phase-icon">{selectedReport.routerOk ? '✅' : '❌'}</span>
                                <span class="phase-name">Router</span>
                                <span class="phase-detail">{selectedReport.routerLatencyMs}ms</span>
                            </div>
                            <div class="phase" class:success={selectedReport.ispOk} class:failed={!selectedReport.ispOk}>
                                <span class="phase-icon">{selectedReport.ispOk ? '✅' : '❌'}</span>
                                <span class="phase-name">ISP</span>
                                <span class="phase-detail">{selectedReport.ispLatencyMs}ms</span>
                            </div>
                            <div class="phase" class:success={selectedReport.dnsOk} class:failed={!selectedReport.dnsOk}>
                                <span class="phase-icon">{selectedReport.dnsOk ? '✅' : '❌'}</span>
                                <span class="phase-name">DNS</span>
                                <span class="phase-detail">{selectedReport.dnsLatencyMs}ms</span>
                            </div>
                        </div>
                    </div>
                {/if}
                
                <!-- Métricas en Vivo (si están) -->
                {#if selectedReport.liveMetrics}
                    <div class="detail-section">
                        <h3>📈 Métricas en Vivo</h3>
                        <div class="live-metrics-grid">
                            <div class="metric-item">
                                <span class="metric-label">Descarga</span>
                                <span class="metric-value">{formatSpeed(selectedReport.liveMetrics.downloadMbps)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Subida</span>
                                <span class="metric-value">{formatSpeed(selectedReport.liveMetrics.uploadMbps)}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Latencia</span>
                                <span class="metric-value">{selectedReport.liveMetrics.latencyMs}ms</span>
                            </div>
                        </div>
                    </div>
                {/if}
                
                {#if selectedReport.recommendation}
                    <div class="detail-section">
                        <h3>💡 Recomendación</h3>
                        <p class="recommendation">{selectedReport.recommendation}</p>
                    </div>
                {/if}
                
                {#if selectedReport.dnsServers && selectedReport.dnsServers.length > 0}
                    <div class="detail-section">
                        <h3>🌐 Servidores DNS</h3>
                        <div class="dns-list">
                            {#each selectedReport.dnsServers as server, i}
                                <span class="dns-server">{i + 1}. {server}</span>
                            {/each}
                        </div>
                    </div>
                {/if}
            </div>
        </div>
    </div>
{/if}

<!-- Modal de Importar -->
{#if showImportModal}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
    <div class="modal-overlay" on:click={closeImportModal} role="dialog" aria-modal="true">
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->
        <div class="modal" on:click|stopPropagation role="document">
            <header class="modal-header">
                <h2>Importar Historial</h2>
                <button class="close-btn" on:click={closeImportModal}>
                    <Icon name="x" size={20} />
                </button>
            </header>
            
            <div class="modal-content">
                <p class="import-hint">Pega el contenido del archivo JSON exportado anteriormente:</p>
                <textarea 
                    class="import-textarea" 
                    bind:value={importJson}
                    placeholder={'{"exportDate": "...", "reports": [...]}'}
                    rows="10"
                ></textarea>
                
                {#if importError}
                    <p class="error-message">{importError}</p>
                {/if}
                
                <div class="modal-actions">
                    <button class="btn btn-secondary" on:click={closeImportModal}>Cancelar</button>
                    <button class="btn btn-primary" on:click={handleImport}>Importar</button>
                </div>
            </div>
        </div>
    </div>
{/if}

<style>
    .reports-tab {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding: 1.5rem;
    }
    
    .actions-bar {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
    }
    
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: all 0.15s;
    }
    
    .btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .btn-primary {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    .btn-primary:hover:not(:disabled) {
        background: #00e6b8;
    }
    
    .btn-secondary {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-secondary, #a0a0a0);
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .btn-secondary:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .stats-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
    }
    
    .stat-card {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-card, #1a1a1a);
        border-radius: 10px;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .stat-card.warning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.2);
    }
    
    .stat-content {
        display: flex;
        flex-direction: column;
    }
    
    .stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
    }
    
    .stat-value.success {
        color: var(--primary, #00d4aa);
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    /* Tests by type section */
    .tests-by-type {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .tests-by-type h3 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary, #a0a0a0);
        margin: 0 0 0.75rem 0;
    }
    
    .type-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }
    
    .type-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
    }
    
    .type-badge .type-icon {
        font-size: 1rem;
    }
    
    .type-badge .type-count {
        font-size: 1rem;
        font-weight: 700;
        color: var(--primary, #00d4aa);
    }
    
    .type-badge .type-name {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .history-section {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 1.25rem;
    }
    
    /* Modal */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 1rem;
    }
    
    .modal {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        width: 100%;
        max-width: 650px;
        max-height: 90vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid var(--border, #3d3d3d);
    }
    
    .modal-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .type-icon-large {
        font-size: 1.75rem;
    }
    
    .modal-title h2 {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0;
    }
    
    .modal-date {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .close-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .close-btn:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .modal-content {
        padding: 1.25rem;
        overflow-y: auto;
    }
    
    /* Health Score Section */
    .health-score-section {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    
    .health-score-badge {
        display: flex;
        align-items: baseline;
        padding: 0.75rem 1rem;
        background: rgba(0, 212, 170, 0.1);
        border: 2px solid var(--score-color);
        border-radius: 12px;
    }
    
    .health-score-badge .score-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--score-color);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .health-score-badge .score-max {
        font-size: 1rem;
        color: var(--text-muted, #666);
    }
    
    .health-info {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .health-status {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .test-duration {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    /* Speed Results */
    .speed-results {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .speed-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.75rem;
        background: var(--bg-card, #1a1a1a);
        border-radius: 8px;
    }
    
    .speed-box .speed-label {
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
    }
    
    .speed-box .speed-value {
        font-size: 0.875rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .speed-box.download .speed-value { color: var(--primary, #00d4aa); }
    .speed-box.upload .speed-value { color: var(--secondary, #a29bfe); }
    .speed-box.ping .speed-value { color: var(--info, #74b9ff); }
    .speed-box.jitter .speed-value { color: var(--warning, #fdcb6e); }
    
    .server-name {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    /* Live Metrics */
    .live-metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.5rem;
    }
    
    .metric-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.5rem;
        background: var(--bg-card, #1a1a1a);
        border-radius: 6px;
    }
    
    .metric-item .metric-label {
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
    }
    
    .metric-item .metric-value {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .detail-section {
        margin-bottom: 1.5rem;
    }
    
    .detail-section:last-child {
        margin-bottom: 0;
    }
    
    .detail-section h3 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary, #a0a0a0);
        margin: 0 0 0.75rem 0;
    }
    
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
    }
    
    .detail-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .detail-item .label {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .detail-item .value {
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
    }
    
    .phases-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
    }
    
    .phase {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.75rem 0.5rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        text-align: center;
    }
    
    .phase.success {
        border: 1px solid rgba(0, 212, 170, 0.3);
    }
    
    .phase.failed {
        border: 1px solid rgba(255, 107, 107, 0.3);
        background: rgba(255, 107, 107, 0.05);
    }
    
    .phase-icon {
        font-size: 1.25rem;
    }
    
    .phase-name {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .phase-detail {
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .recommendation {
        padding: 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        font-size: 0.875rem;
        color: var(--text-secondary, #a0a0a0);
        margin: 0;
        line-height: 1.5;
    }
    
    .dns-list {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
    }
    
    .dns-server {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8125rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    /* Import Modal */
    .import-hint {
        font-size: 0.875rem;
        color: var(--text-secondary, #a0a0a0);
        margin: 0 0 1rem 0;
    }
    
    .import-textarea {
        width: 100%;
        padding: 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8125rem;
        resize: vertical;
    }
    
    .import-textarea:focus {
        outline: none;
        border-color: var(--primary, #00d4aa);
    }
    
    .error-message {
        color: var(--error, #ff6b6b);
        font-size: 0.8125rem;
        margin: 0.75rem 0 0 0;
    }
    
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    @media (max-width: 600px) {
        .phases-grid, .speed-results {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .detail-grid {
            grid-template-columns: 1fr;
        }
        
        .live-metrics-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }
</style>
