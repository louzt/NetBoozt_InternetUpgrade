<!--
    DNSManager.svelte - Componente de gestión DNS para Dashboard
    Muestra estado actual, latencias en tiempo real, y permite reordenar
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { invoke } from '$lib/tauri-bridge';
    import Icon from './Icon.svelte';
    
    // Props
    export let adapter: string = '';
    export let compact: boolean = false;
    export let autoFailoverEnabled: boolean = false;
    
    const dispatch = createEventDispatcher();
    
    // Estado
    let currentDNS: string[] = [];
    let isDHCP = true;
    let loading = true;
    let testingLatency = false;
    let latencies: Record<string, { ms: number; status: 'good' | 'warning' | 'bad' | 'testing' | 'unknown' }> = {};
    let lastLatencyCheck = 0;
    let latencyCheckInterval: ReturnType<typeof setInterval> | null = null;
    
    // DNS conocidos con metadata
    const DNS_PROVIDERS: Record<string, { 
        name: string; 
        icon: string; 
        tier: number;
        description: string;
        primary: string;
        secondary: string;
    }> = {
        '1.1.1.1': { name: 'Cloudflare', icon: '☁️', tier: 1, description: 'El más rápido', primary: '1.1.1.1', secondary: '1.0.0.1' },
        '1.0.0.1': { name: 'Cloudflare', icon: '☁️', tier: 1, description: 'El más rápido', primary: '1.1.1.1', secondary: '1.0.0.1' },
        '8.8.8.8': { name: 'Google', icon: '🔍', tier: 2, description: 'Más confiable', primary: '8.8.8.8', secondary: '8.8.4.4' },
        '8.8.4.4': { name: 'Google', icon: '🔍', tier: 2, description: 'Más confiable', primary: '8.8.8.8', secondary: '8.8.4.4' },
        '9.9.9.9': { name: 'Quad9', icon: '🛡️', tier: 3, description: 'Seguridad', primary: '9.9.9.9', secondary: '149.112.112.112' },
        '149.112.112.112': { name: 'Quad9', icon: '🛡️', tier: 3, description: 'Seguridad', primary: '9.9.9.9', secondary: '149.112.112.112' },
        '208.67.222.222': { name: 'OpenDNS', icon: '🔐', tier: 4, description: 'Filtrado', primary: '208.67.222.222', secondary: '208.67.220.220' },
        '208.67.220.220': { name: 'OpenDNS', icon: '🔐', tier: 4, description: 'Filtrado', primary: '208.67.222.222', secondary: '208.67.220.220' },
        '94.140.14.14': { name: 'AdGuard', icon: '🚫', tier: 5, description: 'Ad-blocking', primary: '94.140.14.14', secondary: '94.140.15.15' },
        '94.140.15.15': { name: 'AdGuard', icon: '🚫', tier: 5, description: 'Ad-blocking', primary: '94.140.14.14', secondary: '94.140.15.15' },
        '185.228.168.9': { name: 'CleanBrowsing', icon: '🧹', tier: 6, description: 'Familia', primary: '185.228.168.9', secondary: '185.228.169.9' },
        '185.228.169.9': { name: 'CleanBrowsing', icon: '🧹', tier: 6, description: 'Familia', primary: '185.228.168.9', secondary: '185.228.169.9' },
    };
    
    // DNS disponibles para agregar
    const availableDNS = [
        { id: 'cloudflare', name: 'Cloudflare', icon: '☁️', primary: '1.1.1.1', secondary: '1.0.0.1', tier: 1 },
        { id: 'google', name: 'Google', icon: '🔍', primary: '8.8.8.8', secondary: '8.8.4.4', tier: 2 },
        { id: 'quad9', name: 'Quad9', icon: '🛡️', primary: '9.9.9.9', secondary: '149.112.112.112', tier: 3 },
        { id: 'opendns', name: 'OpenDNS', icon: '🔐', primary: '208.67.222.222', secondary: '208.67.220.220', tier: 4 },
        { id: 'adguard', name: 'AdGuard', icon: '🚫', primary: '94.140.14.14', secondary: '94.140.15.15', tier: 5 },
        { id: 'cleanbrowsing', name: 'CleanBrowsing', icon: '🧹', primary: '185.228.168.9', secondary: '185.228.169.9', tier: 6 },
    ];
    
    onMount(async () => {
        await loadCurrentDNS();
        // Iniciar chequeo de latencias cada 30 segundos
        latencyCheckInterval = setInterval(() => {
            if (currentDNS.length > 0 && !testingLatency) {
                checkAllLatencies();
            }
        }, 30000);
    });
    
    onDestroy(() => {
        if (latencyCheckInterval) clearInterval(latencyCheckInterval);
    });
    
    async function loadCurrentDNS() {
        loading = true;
        try {
            const result = await invoke<{ servers: string[]; is_dhcp: boolean }>('get_current_dns', { adapter });
            currentDNS = result.servers || [];
            isDHCP = result.is_dhcp;
            
            // Detectar si ya tiene failover configurado (más de 2 DNS = cadena de failover)
            const hasFailoverChain = currentDNS.length > 2;
            if (hasFailoverChain && !autoFailoverEnabled) {
                // Usuario ya tiene una cadena de failover, activar auto-reordenamiento
                dispatch('detectFailover', { enabled: true, count: currentDNS.length });
            }
            
            // Inicializar latencias como unknown
            currentDNS.forEach(dns => {
                if (!latencies[dns]) {
                    latencies[dns] = { ms: 0, status: 'unknown' };
                }
            });
            
            // Medir latencias automáticamente
            if (currentDNS.length > 0) {
                checkAllLatencies();
            }
        } catch (e) {
            console.error('Error cargando DNS:', e);
        } finally {
            loading = false;
        }
    }
    
    async function checkAllLatencies() {
        testingLatency = true;
        lastLatencyCheck = Date.now();
        
        // Marcar todos como testing
        currentDNS.forEach(dns => {
            latencies[dns] = { ...latencies[dns], status: 'testing' };
        });
        latencies = latencies; // trigger reactivity
        
        // Medir en paralelo
        const promises = currentDNS.map(async (dns) => {
            try {
                const result = await invoke<{ latency_ms: number; success: boolean }>('check_single_dns_health', { server: dns });
                if (result.success) {
                    const ms = result.latency_ms;
                    latencies[dns] = {
                        ms,
                        status: ms < 30 ? 'good' : ms < 80 ? 'warning' : 'bad'
                    };
                } else {
                    latencies[dns] = { ms: 999, status: 'bad' };
                }
            } catch {
                latencies[dns] = { ms: 999, status: 'bad' };
            }
        });
        
        await Promise.all(promises);
        latencies = latencies; // trigger reactivity
        testingLatency = false;
        
        // Si auto-failover está activo, reordenar por latencia
        if (autoFailoverEnabled) {
            autoReorderByLatency();
        }
    }
    
    function autoReorderByLatency() {
        // Ordenar DNS por latencia (menor primero)
        const sorted = [...currentDNS].sort((a, b) => {
            const latA = latencies[a]?.ms ?? 999;
            const latB = latencies[b]?.ms ?? 999;
            return latA - latB;
        });
        
        // Si el orden cambió, actualizar
        if (JSON.stringify(sorted) !== JSON.stringify(currentDNS)) {
            dispatch('reorder', sorted);
        }
    }
    
    function getProviderInfo(ip: string): { name: string; icon: string; tier: number; description: string } {
        const known = DNS_PROVIDERS[ip];
        if (known) return known;
        
        if (ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.')) {
            return { name: 'Router', icon: '🏠', tier: 7, description: 'Local' };
        }
        return { name: 'Custom', icon: '🌐', tier: 8, description: 'ISP' };
    }
    
    function formatLatency(ms: number): string {
        if (ms === 0 || ms === 999) return '--';
        return `${Math.round(ms)}ms`;
    }
    
    function getLatencyColor(status: string): string {
        switch (status) {
            case 'good': return 'var(--success, #00ff88)';
            case 'warning': return 'var(--warning, #fdcb6e)';
            case 'bad': return 'var(--error, #ff6b6b)';
            default: return 'var(--text-muted, #666)';
        }
    }
    
    async function setDNS(dnsId: string) {
        const provider = availableDNS.find(d => d.id === dnsId);
        if (!provider || !adapter) return;
        
        loading = true;
        try {
            await invoke('set_dns_servers', { 
                adapter, 
                primary: provider.primary, 
                secondary: provider.secondary 
            });
            await loadCurrentDNS();
            dispatch('change', { dns: [provider.primary, provider.secondary] });
        } catch (e) {
            console.error('Error configurando DNS:', e);
            dispatch('error', e);
        } finally {
            loading = false;
        }
    }
    
    async function resetTodhcp() {
        if (!adapter) return;
        loading = true;
        try {
            await invoke('reset_dns_to_dhcp', { adapter });
            await loadCurrentDNS();
            dispatch('change', { dns: [], dhcp: true });
        } catch (e) {
            console.error('Error reseteando DNS:', e);
            dispatch('error', e);
        } finally {
            loading = false;
        }
    }
    
    async function flushCache() {
        try {
            await invoke('flush_dns_cache');
            dispatch('flush');
        } catch (e) {
            console.error('Error limpiando caché:', e);
        }
    }
    
    function toggleAutoFailover() {
        dispatch('toggleFailover');
    }
    
    // Calcular si un DNS ya está en uso
    function isDNSInUse(primary: string): boolean {
        return currentDNS.includes(primary);
    }
    
    // Tiempo desde último check
    $: timeSinceCheck = lastLatencyCheck > 0 
        ? Math.floor((Date.now() - lastLatencyCheck) / 1000) 
        : 0;
</script>

<div class="dns-manager" class:compact>
    <div class="dns-header">
        <div class="header-title">
            <Icon name="globe" size={compact ? 16 : 18} />
            <h3>DNS</h3>
            {#if isDHCP}
                <span class="dns-mode dhcp">DHCP</span>
            {:else}
                <span class="dns-mode static">Estático</span>
            {/if}
        </div>
        <div class="header-actions">
            <label class="failover-toggle" title="Auto-reordenar por latencia">
                <input type="checkbox" checked={autoFailoverEnabled} on:change={toggleAutoFailover} />
                <span class="toggle-track"></span>
                {#if !compact}<span class="toggle-label">Auto</span>{/if}
            </label>
            <button class="icon-btn" on:click={checkAllLatencies} disabled={testingLatency} title="Medir latencias">
                <Icon name="refresh-cw" size={14} className={testingLatency ? 'spinning' : ''} />
            </button>
        </div>
    </div>
    
    <!-- DNS Activos con latencias -->
    <div class="current-dns">
        {#if loading}
            <div class="loading-state">
                <span class="spinner"></span>
                Cargando...
            </div>
        {:else if currentDNS.length === 0}
            <div class="empty-state">
                <span>Sin DNS configurado</span>
            </div>
        {:else}
            <div class="dns-list">
                {#each currentDNS as dns, index}
                    {@const info = getProviderInfo(dns)}
                    {@const lat = latencies[dns] || { ms: 0, status: 'unknown' }}
                    <div class="dns-item" class:primary={index === 0}>
                        <div class="dns-rank">
                            {#if index === 0}
                                <span class="rank-badge primary">1°</span>
                            {:else}
                                <span class="rank-badge">{index + 1}°</span>
                            {/if}
                        </div>
                        <div class="dns-info">
                            <span class="dns-icon">{info.icon}</span>
                            <div class="dns-details">
                                <span class="dns-name">{info.name}</span>
                                <span class="dns-ip">{dns}</span>
                            </div>
                        </div>
                        <div class="dns-latency" style="color: {getLatencyColor(lat.status)}">
                            {#if lat.status === 'testing'}
                                <span class="spinner-mini"></span>
                            {:else}
                                <span class="latency-value">{formatLatency(lat.ms)}</span>
                                {#if lat.status === 'good'}
                                    <Icon name="check-circle" size={12} />
                                {:else if lat.status === 'warning'}
                                    <Icon name="alert-circle" size={12} />
                                {:else if lat.status === 'bad'}
                                    <Icon name="x-circle" size={12} />
                                {/if}
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
    
    {#if !compact}
        <!-- DNS Disponibles -->
        <div class="available-dns">
            <h4>Servidores Disponibles</h4>
            <div class="dns-grid">
                {#each availableDNS as dns}
                    {@const inUse = isDNSInUse(dns.primary)}
                    {@const providerLatency = latencies[dns.primary]}
                    <button 
                        class="dns-option" 
                        class:in-use={inUse}
                        class:has-latency={providerLatency?.ms > 0}
                        disabled={loading}
                        on:click={() => setDNS(dns.id)}
                        title="{dns.name} - {dns.primary} / {dns.secondary}{providerLatency?.ms ? ` (${providerLatency.ms}ms)` : ''}"
                    >
                        <span class="option-icon">{dns.icon}</span>
                        <span class="option-name">{dns.name}</span>
                        <span class="option-tier">T{dns.tier}</span>
                        {#if inUse}
                            <span class="in-use-badge">✓ Activo</span>
                        {/if}
                    </button>
                {/each}
            </div>
        </div>
        
        <!-- Acciones -->
        <div class="dns-actions">
            <button class="btn btn-ghost" on:click={resetTodhcp} disabled={loading || isDHCP} title="Resetear DNS a automático (DHCP)">
                <Icon name="rotate-ccw" size={14} />
                Automático
            </button>
            <button class="btn btn-ghost" on:click={flushCache} disabled={loading} title="Limpiar caché DNS del sistema">
                <Icon name="trash-2" size={14} />
                Limpiar Caché
            </button>
        </div>
    {:else}
        <!-- Versión compacta: solo botones rápidos -->
        <div class="compact-actions">
            {#each availableDNS.slice(0, 3) as dns}
                {@const inUse = isDNSInUse(dns.primary)}
                <button 
                    class="quick-dns" 
                    class:active={inUse}
                    disabled={loading}
                    on:click={() => setDNS(dns.id)}
                    title={dns.name}
                >
                    {dns.icon}
                </button>
            {/each}
            <button class="quick-dns" on:click={() => dispatch('openFullDNS')} title="Ver más">
                <Icon name="more-horizontal" size={14} />
            </button>
        </div>
    {/if}
</div>

<style>
    .dns-manager {
        display: flex;
        flex-direction: column;
        height: 100%;
    }
    
    .dns-manager.compact {
        /* Modo compacto: menos espaciado interno */
        gap: 0.5rem;
    }
    
    .dns-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .header-title h3 {
        font-size: 0.9375rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0;
    }
    
    .compact .header-title h3 {
        font-size: 0.875rem;
    }
    
    .dns-mode {
        font-size: 0.625rem;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .dns-mode.dhcp {
        background: rgba(253, 203, 110, 0.15);
        color: var(--warning, #fdcb6e);
    }
    
    .dns-mode.static {
        background: rgba(0, 212, 170, 0.15);
        color: var(--primary, #00d4aa);
    }
    
    .header-actions {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .failover-toggle {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        cursor: pointer;
    }
    
    .failover-toggle input { display: none; }
    
    .toggle-track {
        width: 28px;
        height: 16px;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        position: relative;
        transition: background 0.2s;
    }
    
    .toggle-track::after {
        content: '';
        position: absolute;
        width: 12px;
        height: 12px;
        background: var(--text-muted, #666);
        border-radius: 50%;
        top: 2px;
        left: 2px;
        transition: transform 0.2s, background 0.2s;
    }
    
    .failover-toggle input:checked + .toggle-track {
        background: var(--primary, #00d4aa);
    }
    
    .failover-toggle input:checked + .toggle-track::after {
        transform: translateX(12px);
        background: #fff;
    }
    
    .toggle-label {
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
    }
    
    .icon-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-secondary, #a0a0a0);
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .icon-btn:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .icon-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    :global(.spinning) {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* DNS List */
    .current-dns {
        margin-bottom: 0.75rem;
    }
    
    .loading-state, .empty-state {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 1rem;
        color: var(--text-muted, #666);
        font-size: 0.8125rem;
    }
    
    .spinner {
        width: 16px;
        height: 16px;
        border: 2px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .dns-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .dns-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        border-left: 3px solid var(--border, #3d3d3d);
    }
    
    .dns-item.primary {
        border-left-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.05);
    }
    
    .dns-rank {
        min-width: 24px;
    }
    
    .rank-badge {
        font-size: 0.625rem;
        font-weight: 700;
        color: var(--text-muted, #666);
    }
    
    .rank-badge.primary {
        color: var(--primary, #00d4aa);
    }
    
    .dns-info {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        min-width: 0;
    }
    
    .dns-icon {
        font-size: 1rem;
        flex-shrink: 0;
    }
    
    .dns-details {
        display: flex;
        flex-direction: column;
        min-width: 0;
    }
    
    .dns-name {
        font-size: 0.8125rem;
        font-weight: 500;
        color: var(--text-primary, #fff);
    }
    
    .dns-ip {
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .dns-latency {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .spinner-mini {
        width: 12px;
        height: 12px;
        border: 2px solid var(--border, #3d3d3d);
        border-top-color: var(--text-muted, #666);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    /* Available DNS */
    .available-dns {
        flex: 1;
        margin-bottom: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border, #3d3d3d);
        min-height: 0;
        overflow-y: auto;
    }
    
    .available-dns h4 {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary, #a0a0a0);
        margin: 0 0 0.5rem 0;
    }
    
    .dns-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.5rem;
    }
    
    @media (max-width: 600px) {
        .dns-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    .dns-option {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.5rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s;
        position: relative;
    }
    
    .dns-option:hover:not(:disabled) {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.1);
    }
    
    .dns-option:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .dns-option.in-use {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.15);
    }
    
    .dns-option.in-use:hover:not(:disabled) {
        background: rgba(0, 212, 170, 0.2);
    }
    
    .in-use-badge {
        position: absolute;
        top: 2px;
        right: 2px;
        font-size: 0.5rem;
        padding: 0.1rem 0.25rem;
        background: var(--primary, #00d4aa);
        color: #000;
        border-radius: 3px;
        font-weight: 700;
    }
    
    .option-icon {
        font-size: 1.25rem;
    }
    
    .option-name {
        font-size: 0.6875rem;
        font-weight: 500;
        color: var(--text-primary, #fff);
    }
    
    .option-tier {
        font-size: 0.5625rem;
        color: var(--text-muted, #666);
        font-weight: 600;
    }
    
    :global(.in-use-check) {
        position: absolute;
        top: 4px;
        right: 4px;
        color: var(--primary, #00d4aa);
    }
    
    /* Actions */
    .dns-actions {
        display: flex;
        gap: 0.5rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: all 0.15s;
    }
    
    .btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .btn-ghost {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-secondary, #a0a0a0);
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .btn-ghost:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    /* Compact Actions */
    .compact-actions {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
    }
    
    .quick-dns {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        font-size: 1.125rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .quick-dns:hover:not(:disabled) {
        border-color: var(--primary, #00d4aa);
        transform: translateY(-2px);
    }
    
    .quick-dns.active {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.15);
    }
    
    .quick-dns:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
