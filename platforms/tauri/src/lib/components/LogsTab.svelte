<!--
    LogsTab.svelte - Vista de logs del sistema con filtros
    By LOUST
-->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { invoke } from '$lib/tauri-bridge';
    import Icon from './Icon.svelte';
    
    // Tipos
    interface LogEntry {
        id: string;
        timestamp: number;
        level: 'info' | 'warning' | 'error' | 'debug';
        category: 'dns' | 'network' | 'diagnostic' | 'optimization' | 'system';
        message: string;
        details?: Record<string, any>;
    }
    
    // Estado
    let logs: LogEntry[] = [];
    let filteredLogs: LogEntry[] = [];
    let loading = true;
    let autoRefresh = true;
    let refreshInterval: ReturnType<typeof setInterval> | null = null;
    
    // Filtros
    let levelFilter: string = 'all';
    let categoryFilter: string = 'all';
    let searchQuery: string = '';
    let dateRangeFilter: string = 'today'; // today, week, all
    
    // Storage key
    const STORAGE_KEY_LOGS = 'netboozt_logs';
    const MAX_LOGS = 500;
    
    // ========== LIFECYCLE ==========
    onMount(() => {
        loadLogs();
        if (autoRefresh) {
            refreshInterval = setInterval(loadLogs, 10000);
        }
    });
    
    onDestroy(() => {
        if (refreshInterval) clearInterval(refreshInterval);
    });
    
    // ========== LOG OPERATIONS ==========
    function loadLogs() {
        loading = true;
        try {
            if (typeof localStorage !== 'undefined') {
                const saved = localStorage.getItem(STORAGE_KEY_LOGS);
                if (saved) {
                    logs = JSON.parse(saved);
                } else {
                    logs = generateSampleLogs();
                    saveLogs();
                }
            }
        } catch (e) {
            console.error('Error cargando logs:', e);
            logs = generateSampleLogs();
        }
        applyFilters();
        loading = false;
    }
    
    function saveLogs() {
        if (typeof localStorage === 'undefined') return;
        try {
            // Limitar cantidad de logs
            const toSave = logs.slice(-MAX_LOGS);
            localStorage.setItem(STORAGE_KEY_LOGS, JSON.stringify(toSave));
        } catch (e) {
            console.error('Error guardando logs:', e);
        }
    }
    
    // Función para agregar logs desde otros componentes
    export function addLog(level: LogEntry['level'], category: LogEntry['category'], message: string, details?: Record<string, any>) {
        const entry: LogEntry = {
            id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: Date.now(),
            level,
            category,
            message,
            details
        };
        
        logs = [...logs, entry].slice(-MAX_LOGS);
        saveLogs();
        applyFilters();
    }
    
    function clearLogs() {
        if (confirm('¿Eliminar todos los logs?')) {
            logs = [];
            saveLogs();
            applyFilters();
        }
    }
    
    function exportLogs() {
        const data = JSON.stringify(filteredLogs, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `netboozt_logs_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    // ========== FILTERS ==========
    function applyFilters() {
        const now = Date.now();
        const dayMs = 24 * 60 * 60 * 1000;
        
        filteredLogs = logs.filter(log => {
            // Level filter
            if (levelFilter !== 'all' && log.level !== levelFilter) return false;
            
            // Category filter
            if (categoryFilter !== 'all' && log.category !== categoryFilter) return false;
            
            // Date filter
            if (dateRangeFilter === 'today' && log.timestamp < now - dayMs) return false;
            if (dateRangeFilter === 'week' && log.timestamp < now - (7 * dayMs)) return false;
            
            // Search filter
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                if (!log.message.toLowerCase().includes(query)) return false;
            }
            
            return true;
        });
        
        // Ordenar por más recientes primero
        filteredLogs = filteredLogs.sort((a, b) => b.timestamp - a.timestamp);
    }
    
    // Reactivos para filtros
    $: levelFilter, categoryFilter, searchQuery, dateRangeFilter, applyFilters();
    
    // ========== HELPERS ==========
    function formatTime(timestamp: number): string {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }
    
    function formatDate(timestamp: number): string {
        const date = new Date(timestamp);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        if (date.toDateString() === today.toDateString()) return 'Hoy';
        if (date.toDateString() === yesterday.toDateString()) return 'Ayer';
        return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' });
    }
    
    function getLevelIcon(level: string): string {
        switch (level) {
            case 'info': return 'info';
            case 'warning': return 'alert-triangle';
            case 'error': return 'x-circle';
            case 'debug': return 'code';
            default: return 'info';
        }
    }
    
    function getLevelColor(level: string): string {
        switch (level) {
            case 'info': return 'var(--primary, #00d4aa)';
            case 'warning': return 'var(--warning, #fdcb6e)';
            case 'error': return 'var(--error, #ff6b6b)';
            case 'debug': return 'var(--text-muted, #888)';
            default: return 'var(--text-secondary, #a0a0a0)';
        }
    }
    
    function getCategoryIcon(category: string): string {
        switch (category) {
            case 'dns': return 'globe';
            case 'network': return 'wifi';
            case 'diagnostic': return 'activity';
            case 'optimization': return 'zap';
            case 'system': return 'cpu';
            default: return 'file-text';
        }
    }
    
    function getCategoryLabel(category: string): string {
        const labels: Record<string, string> = {
            dns: 'DNS',
            network: 'Red',
            diagnostic: 'Diagnóstico',
            optimization: 'Optimización',
            system: 'Sistema'
        };
        return labels[category] || category;
    }
    
    // ========== SAMPLE DATA ==========
    function generateSampleLogs(): LogEntry[] {
        const now = Date.now();
        const hour = 60 * 60 * 1000;
        
        return [
            { id: 'l1', timestamp: now - (5 * 60000), level: 'info', category: 'dns', message: 'DNS cambiado a Cloudflare (1.1.1.1)', details: { latency: 12 } },
            { id: 'l2', timestamp: now - (15 * 60000), level: 'info', category: 'network', message: 'Adaptador detectado: Intel Wi-Fi 6 AX201', details: { speed: '866 Mbps' } },
            { id: 'l3', timestamp: now - (30 * 60000), level: 'warning', category: 'dns', message: 'Latencia alta en Google DNS (85ms)', details: { server: '8.8.8.8', latency: 85 } },
            { id: 'l4', timestamp: now - (45 * 60000), level: 'info', category: 'optimization', message: 'TCP optimizaciones aplicadas: RSC, RSS, Autotuning' },
            { id: 'l5', timestamp: now - hour, level: 'error', category: 'dns', message: 'Timeout alcanzando 9.9.9.9', details: { timeout: 5000 } },
            { id: 'l6', timestamp: now - (2 * hour), level: 'info', category: 'diagnostic', message: 'Diagnóstico completado: 5/5 fases OK' },
            { id: 'l7', timestamp: now - (3 * hour), level: 'debug', category: 'system', message: 'NetBoozt iniciado correctamente' },
            { id: 'l8', timestamp: now - (5 * hour), level: 'warning', category: 'network', message: 'Señal WiFi débil detectada', details: { strength: '-75 dBm' } },
            { id: 'l9', timestamp: now - (8 * hour), level: 'info', category: 'dns', message: 'Auto-failover: cambiando a Google DNS' },
            { id: 'l10', timestamp: now - (24 * hour), level: 'info', category: 'optimization', message: 'ECN habilitado para mejorar congestión' },
        ];
    }
    
    // Toggle auto-refresh
    function toggleAutoRefresh() {
        autoRefresh = !autoRefresh;
        if (autoRefresh && !refreshInterval) {
            refreshInterval = setInterval(loadLogs, 10000);
        } else if (!autoRefresh && refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    }
</script>

<div class="logs-tab">
    <!-- Header -->
    <div class="logs-header">
        <div class="header-title">
            <Icon name="scroll-text" size={20} />
            <h2>Logs del Sistema</h2>
            <span class="log-count">{filteredLogs.length} registros</span>
        </div>
        <div class="header-actions">
            <button class="icon-btn" on:click={toggleAutoRefresh} class:active={autoRefresh} title="Auto-refresh">
                <Icon name="refresh" size={14} className={autoRefresh ? 'spinning-slow' : ''} />
            </button>
            <button class="icon-btn" on:click={exportLogs} title="Exportar logs">
                <Icon name="download" size={14} />
            </button>
            <button class="icon-btn danger" on:click={clearLogs} title="Limpiar logs">
                <Icon name="trash-2" size={14} />
            </button>
        </div>
    </div>
    
    <!-- Filters -->
    <div class="filters-bar">
        <div class="filter-group">
            <label for="search">
                <Icon name="search" size={14} />
            </label>
            <input 
                type="text" 
                id="search"
                bind:value={searchQuery}
                placeholder="Buscar en logs..."
            />
        </div>
        
        <div class="filter-group">
            <Icon name="filter" size={14} />
            <select bind:value={levelFilter}>
                <option value="all">Todos los niveles</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
                <option value="debug">Debug</option>
            </select>
        </div>
        
        <div class="filter-group">
            <Icon name="layers" size={14} />
            <select bind:value={categoryFilter}>
                <option value="all">Todas las categorías</option>
                <option value="dns">DNS</option>
                <option value="network">Red</option>
                <option value="diagnostic">Diagnóstico</option>
                <option value="optimization">Optimización</option>
                <option value="system">Sistema</option>
            </select>
        </div>
        
        <div class="filter-group">
            <Icon name="calendar" size={14} />
            <select bind:value={dateRangeFilter}>
                <option value="today">Hoy</option>
                <option value="week">Esta semana</option>
                <option value="all">Todo</option>
            </select>
        </div>
    </div>
    
    <!-- Logs List -->
    <div class="logs-container">
        {#if loading}
            <div class="loading-state">
                <span class="spinner"></span>
                Cargando logs...
            </div>
        {:else if filteredLogs.length === 0}
            <div class="empty-state">
                <Icon name="file-text" size={32} />
                <p>No hay logs que mostrar</p>
                {#if searchQuery || levelFilter !== 'all' || categoryFilter !== 'all'}
                    <button class="btn-ghost" on:click={() => { searchQuery = ''; levelFilter = 'all'; categoryFilter = 'all'; }}>
                        Limpiar filtros
                    </button>
                {/if}
            </div>
        {:else}
            <div class="logs-list">
                {#each filteredLogs as log (log.id)}
                    <div class="log-entry {log.level}">
                        <div class="log-time">
                            <span class="date">{formatDate(log.timestamp)}</span>
                            <span class="time">{formatTime(log.timestamp)}</span>
                        </div>
                        <div class="log-level" style="color: {getLevelColor(log.level)}">
                            <Icon name={getLevelIcon(log.level)} size={14} />
                        </div>
                        <div class="log-category">
                            <span class="category-badge {log.category}">
                                <Icon name={getCategoryIcon(log.category)} size={10} />
                                {getCategoryLabel(log.category)}
                            </span>
                        </div>
                        <div class="log-message">
                            {log.message}
                            {#if log.details}
                                <span class="log-details">
                                    {Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(' • ')}
                                </span>
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
    .logs-tab {
        display: flex;
        flex-direction: column;
        height: 100%;
        gap: 1rem;
    }
    
    /* Header */
    .logs-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .header-title h2 {
        margin: 0;
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .log-count {
        font-size: 0.75rem;
        padding: 0.2rem 0.5rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
        color: var(--text-muted, #888);
    }
    
    .header-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .icon-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-muted, #888);
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .icon-btn:hover { 
        background: var(--primary, #00d4aa); 
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .icon-btn.active {
        background: rgba(0, 212, 170, 0.15);
        border-color: var(--primary, #00d4aa);
        color: var(--primary, #00d4aa);
    }
    
    .icon-btn.danger:hover {
        background: var(--error, #ff6b6b);
        border-color: var(--error, #ff6b6b);
    }
    
    :global(.spinning-slow) { animation: spin 2s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    /* Filters */
    .filters-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        padding: 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .filter-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-muted, #888);
    }
    
    .filter-group input,
    .filter-group select {
        padding: 0.4rem 0.75rem;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-primary, #fff);
        font-size: 0.8125rem;
        min-width: 120px;
    }
    
    .filter-group input {
        min-width: 200px;
    }
    
    .filter-group input:focus,
    .filter-group select:focus {
        outline: none;
        border-color: var(--primary, #00d4aa);
    }
    
    .filter-group select {
        cursor: pointer;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 0.5rem center;
        padding-right: 2rem;
    }
    
    /* Logs Container */
    .logs-container {
        flex: 1;
        overflow-y: auto;
        background: var(--bg-card, #1a1a1a);
        border-radius: 8px;
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .loading-state,
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 3rem;
        color: var(--text-muted, #666);
    }
    
    .empty-state p {
        margin: 0;
        font-size: 0.875rem;
    }
    
    .spinner {
        width: 24px;
        height: 24px;
        border: 2px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .btn-ghost {
        padding: 0.4rem 0.75rem;
        background: transparent;
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .btn-ghost:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    /* Logs List */
    .logs-list {
        display: flex;
        flex-direction: column;
    }
    
    .log-entry {
        display: grid;
        grid-template-columns: 5rem 2rem 6rem 1fr;
        gap: 0.75rem;
        padding: 0.6rem 1rem;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        transition: background 0.1s;
    }
    
    .log-entry:hover { background: rgba(255, 255, 255, 0.02); }
    .log-entry:last-child { border-bottom: none; }
    
    .log-entry.error { background: rgba(255, 107, 107, 0.05); }
    .log-entry.warning { background: rgba(253, 203, 110, 0.03); }
    
    .log-time {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }
    
    .log-time .date {
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
    }
    
    .log-time .time {
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .log-level {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .log-category {
        display: flex;
    }
    
    .category-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.15rem 0.5rem;
        font-size: 0.625rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.05);
        color: var(--text-muted, #888);
    }
    
    .category-badge.dns { background: rgba(0, 212, 170, 0.1); color: var(--primary, #00d4aa); }
    .category-badge.network { background: rgba(100, 100, 255, 0.1); color: #6b7cff; }
    .category-badge.diagnostic { background: rgba(253, 203, 110, 0.1); color: var(--warning, #fdcb6e); }
    .category-badge.optimization { background: rgba(255, 107, 107, 0.1); color: #ff9f9f; }
    .category-badge.system { background: rgba(150, 150, 150, 0.1); color: var(--text-secondary, #a0a0a0); }
    
    .log-message {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
        font-size: 0.8125rem;
        color: var(--text-primary, #fff);
    }
    
    .log-details {
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
        font-family: 'JetBrains Mono', monospace;
    }
</style>
