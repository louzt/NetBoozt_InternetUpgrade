<!--
    DNSManager.svelte - Componente de gestión DNS para Dashboard
    Tabla moderna con drag & drop, latencias, protocolos y recomendaciones
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { invoke, isTauriAvailable } from '$lib/tauri-bridge';
    import Icon from './Icon.svelte';
    
    // Props
    export let adapter: string = '';
    export let compact: boolean = false;
    export let autoFailoverEnabled: boolean = false;
    
    const dispatch = createEventDispatcher();
    
    // Claves de localStorage
    const STORAGE_KEY_DNS_BOOSTED = 'netboozt_dns_boosted';
    const STORAGE_KEY_DNS_HISTORY = 'netboozt_dns_latency_history';
    const STORAGE_KEY_DNS_ACTIVE_STATE = 'netboozt_dns_active_state';
    
    // Tipos
    interface DnsMetrics {
        ms: number;
        status: 'good' | 'warning' | 'bad' | 'testing' | 'unknown';
        protocol: string;
        avgMs: number;
        checksCount: number;
        lastCheck: number;
    }
    
    interface DnsProvider {
        id: string;
        name: string;
        primary: string;
        secondary: string;
        tier: number;
        protocol: string;
        port: number;
    }
    
    // Estado
    let currentDNS: string[] = [];
    let isDHCP = true;
    let loading = true;
    let testingLatency = false;
    let metrics: Record<string, DnsMetrics> = {};
    let lastLatencyCheck = 0;
    let latencyCheckInterval: ReturnType<typeof setInterval> | null = null;
    
    // Drag & Drop state
    let draggedDns: string | null = null;
    let dragOverTarget: string | null = null;
    let isDragging = false;
    
    // DNS proveedores con info extendida
    const DEFAULT_DNS_PROVIDERS: DnsProvider[] = [
        { id: 'cloudflare', name: 'Cloudflare', primary: '1.1.1.1', secondary: '1.0.0.1', tier: 1, protocol: 'DoH/DoT', port: 53 },
        { id: 'google', name: 'Google', primary: '8.8.8.8', secondary: '8.8.4.4', tier: 2, protocol: 'DoH/DoT', port: 53 },
        { id: 'quad9', name: 'Quad9', primary: '9.9.9.9', secondary: '149.112.112.112', tier: 3, protocol: 'DoH/DoT', port: 53 },
        { id: 'opendns', name: 'OpenDNS', primary: '208.67.222.222', secondary: '208.67.220.220', tier: 4, protocol: 'DNSCrypt', port: 443 },
        { id: 'adguard', name: 'AdGuard', primary: '94.140.14.14', secondary: '94.140.15.15', tier: 5, protocol: 'DoH/DoT', port: 53 },
        { id: 'cleanbrowsing', name: 'CleanBrowsing', primary: '185.228.168.9', secondary: '185.228.169.9', tier: 6, protocol: 'DoH', port: 53 },
    ];
    
    // DNS personalizados del usuario
    const STORAGE_KEY_CUSTOM_DNS = 'netboozt_custom_dns';
    let customDnsProviders: DnsProvider[] = [];
    
    // Estado del modal de agregar/editar DNS
    let showDnsModal = false;
    let editingDns: DnsProvider | null = null;
    let dnsForm = {
        name: '',
        primary: '',
        secondary: '',
        protocol: 'UDP',
        port: 53
    };
    let dnsFormError = '';
    
    // Lista combinada de proveedores (default + custom)
    let DNS_PROVIDERS: DnsProvider[] = [...DEFAULT_DNS_PROVIDERS];
    
    // Actualizar DNS_PROVIDERS cuando cambian los custom
    $: DNS_PROVIDERS = [...DEFAULT_DNS_PROVIDERS, ...customDnsProviders];
    
    // Cargar DNS personalizados
    function loadCustomDns() {
        if (typeof localStorage === 'undefined') return;
        try {
            const saved = localStorage.getItem(STORAGE_KEY_CUSTOM_DNS);
            if (saved) {
                customDnsProviders = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Error cargando DNS personalizados:', e);
        }
    }
    
    // Guardar DNS personalizados
    function saveCustomDns() {
        if (typeof localStorage === 'undefined') return;
        try {
            localStorage.setItem(STORAGE_KEY_CUSTOM_DNS, JSON.stringify(customDnsProviders));
        } catch (e) {
            console.warn('Error guardando DNS personalizados:', e);
        }
    }
    
    // Validar IP
    function isValidIP(ip: string): boolean {
        const ipv4Pattern = /^(\d{1,3}\.){3}\d{1,3}$/;
        if (!ipv4Pattern.test(ip)) return false;
        const parts = ip.split('.').map(Number);
        return parts.every(p => p >= 0 && p <= 255);
    }
    
    // Abrir modal para agregar DNS
    function openAddDnsModal() {
        editingDns = null;
        dnsForm = { name: '', primary: '', secondary: '', protocol: 'UDP', port: 53 };
        dnsFormError = '';
        showDnsModal = true;
    }
    
    // Abrir modal para editar DNS (solo custom)
    function openEditDnsModal(provider: DnsProvider) {
        editingDns = provider;
        dnsForm = {
            name: provider.name,
            primary: provider.primary,
            secondary: provider.secondary,
            protocol: provider.protocol,
            port: provider.port
        };
        dnsFormError = '';
        showDnsModal = true;
    }
    
    // Guardar DNS (agregar o editar)
    async function saveDnsForm() {
        // Validaciones
        dnsFormError = ''; // Limpiar error previo
        
        if (!dnsForm.name.trim()) {
            dnsFormError = 'Ingresa un nombre para el servidor DNS';
            return;
        }
        if (!isValidIP(dnsForm.primary)) {
            dnsFormError = 'IP primaria inválida (ej: 192.168.1.1)';
            return;
        }
        if (dnsForm.secondary && !isValidIP(dnsForm.secondary)) {
            dnsFormError = 'IP secundaria inválida';
            return;
        }
        
        // Verificar que no exista ya
        const existingDefault = DEFAULT_DNS_PROVIDERS.find(p => 
            p.primary === dnsForm.primary || p.secondary === dnsForm.primary
        );
        if (existingDefault && (!editingDns || editingDns.primary !== dnsForm.primary)) {
            dnsFormError = `Esta IP ya pertenece a ${existingDefault.name}`;
            return;
        }
        
        if (editingDns) {
            // Editar existente
            const idx = customDnsProviders.findIndex(p => p.id === editingDns!.id);
            if (idx !== -1) {
                customDnsProviders[idx] = {
                    ...editingDns,
                    name: dnsForm.name.trim(),
                    primary: dnsForm.primary,
                    secondary: dnsForm.secondary || dnsForm.primary,
                    protocol: dnsForm.protocol,
                    port: dnsForm.port
                };
                customDnsProviders = [...customDnsProviders];
                dispatch('showNotification', { type: 'success', message: `✓ DNS "${dnsForm.name}" actualizado` });
            }
        } else {
            // Agregar nuevo
            const newDns: DnsProvider = {
                id: `custom-${Date.now()}`,
                name: dnsForm.name.trim(),
                primary: dnsForm.primary,
                secondary: dnsForm.secondary || dnsForm.primary,
                tier: 7 + customDnsProviders.length,
                protocol: dnsForm.protocol,
                port: dnsForm.port
            };
            customDnsProviders = [...customDnsProviders, newDns];
            dispatch('showNotification', { type: 'success', message: `✓ DNS "${newDns.name}" agregado` });
        }
        
        saveCustomDns();
        showDnsModal = false;
        
        // Reinicializar métricas para incluir el nuevo DNS
        initializeMetrics();
        
        // Medir latencia del nuevo DNS
        await measureAllDNS();
    }
    
    // Eliminar DNS personalizado
    function deleteCustomDns(provider: DnsProvider) {
        if (!confirm(`¿Eliminar "${provider.name}" de los DNS personalizados?`)) return;
        customDnsProviders = customDnsProviders.filter(p => p.id !== provider.id);
        saveCustomDns();
    }
    
    // Verificar si es DNS personalizado
    function isCustomDns(provider: DnsProvider): boolean {
        return provider.id.startsWith('custom-');
    }
    
    // Estado del modo NetBoozt DNS
    let netbooztDnsActive = false;
    let activatingBoostedDns = false;
    
    // ========== PERSISTENCIA ==========
    function saveState() {
        if (typeof localStorage === 'undefined') return;
        try {
            // Guardar estado completo del DNS Boosted
            localStorage.setItem(STORAGE_KEY_DNS_BOOSTED, JSON.stringify({
                active: netbooztDnsActive,
                dns: currentDNS,
                adapter: adapter,
                timestamp: Date.now()
            }));
            // También guardar estado activo por separado (para restaurar rápido)
            localStorage.setItem(STORAGE_KEY_DNS_ACTIVE_STATE, JSON.stringify({
                wasActive: netbooztDnsActive,
                lastAdapter: adapter
            }));
        } catch (e) {
            console.warn('Error guardando estado DNS:', e);
        }
    }
    
    function loadSavedState(): { active: boolean; dns: string[]; adapter: string } | null {
        if (typeof localStorage === 'undefined') return null;
        try {
            const saved = localStorage.getItem(STORAGE_KEY_DNS_BOOSTED);
            if (saved) {
                const data = JSON.parse(saved);
                // Verificar que sea del mismo adaptador y que no haya pasado más de 24h
                if (data.adapter === adapter && Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
                    return data;
                }
            }
        } catch (e) {
            console.warn('Error cargando estado DNS:', e);
        }
        return null;
    }
    
    function loadActiveState(): { wasActive: boolean; lastAdapter: string } | null {
        if (typeof localStorage === 'undefined') return null;
        try {
            const saved = localStorage.getItem(STORAGE_KEY_DNS_ACTIVE_STATE);
            if (saved) {
                return JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Error cargando estado activo DNS:', e);
        }
        return null;
    }
    
    function saveMetricsHistory() {
        if (typeof localStorage === 'undefined') return;
        try {
            const history: Record<string, { avgMs: number; checksCount: number }> = {};
            for (const [ip, m] of Object.entries(metrics)) {
                history[ip] = { avgMs: m.avgMs, checksCount: m.checksCount };
            }
            localStorage.setItem(STORAGE_KEY_DNS_HISTORY, JSON.stringify(history));
        } catch (e) {
            console.warn('Error guardando historial DNS:', e);
        }
    }
    
    function loadMetricsHistory() {
        if (typeof localStorage === 'undefined') return;
        try {
            const saved = localStorage.getItem(STORAGE_KEY_DNS_HISTORY);
            if (saved) {
                const history = JSON.parse(saved);
                for (const [ip, data] of Object.entries(history)) {
                    if (metrics[ip]) {
                        metrics[ip].avgMs = (data as any).avgMs || 0;
                        metrics[ip].checksCount = (data as any).checksCount || 0;
                    }
                }
            }
        } catch (e) {
            console.warn('Error cargando historial DNS:', e);
        }
    }
    
    // ========== LIFECYCLE ==========
    onMount(async () => {
        loadCustomDns(); // Cargar DNS personalizados primero
        initializeMetrics();
        loadMetricsHistory();
        await loadCurrentDNS();
        
        // Verificar estado guardado y restaurar si corresponde
        const savedState = loadSavedState();
        const activeState = loadActiveState();
        
        // Si tenemos estado activo guardado y el DNS actual está en DHCP
        // significa que la app se reinició pero el DNS se perdió
        if (activeState?.wasActive && isDHCP && adapter === activeState.lastAdapter) {
            console.log('🔄 DNS Boosted was active last session, DNS is now DHCP - offering to restore');
            // No restaurar automáticamente, pero mostrar que estaba activo
            dispatch('showNotification', { 
                type: 'info', 
                message: '💡 DNS Boosted estaba activo. ¿Deseas reactivarlo?' 
            });
        } else if (savedState && savedState.active && !isDHCP) {
            // El DNS ya está configurado correctamente, solo actualizar estado
            netbooztDnsActive = true;
            console.log('✅ DNS Boosted already active from last session');
        }
        
        await measureAllDNS();
        latencyCheckInterval = setInterval(() => {
            if (!testingLatency) measureAllDNS();
        }, 30000);
    });
    
    onDestroy(() => {
        if (latencyCheckInterval) clearInterval(latencyCheckInterval);
        saveMetricsHistory();
    });
    
    function initializeMetrics() {
        // Incluir todos los proveedores: default + custom
        const allProviders = [...DEFAULT_DNS_PROVIDERS, ...customDnsProviders];
        for (const provider of allProviders) {
            for (const ip of [provider.primary, provider.secondary]) {
                if (ip && !metrics[ip]) {
                    metrics[ip] = {
                        ms: 0,
                        status: 'unknown',
                        protocol: provider.protocol,
                        avgMs: 0,
                        checksCount: 0,
                        lastCheck: 0
                    };
                }
            }
        }
        metrics = metrics; // Forzar reactividad
    }
    
    // ========== DNS OPERATIONS ==========
    async function loadCurrentDNS() {
        loading = true;
        try {
            const result = await invoke<{ servers: string[]; is_dhcp: boolean }>('get_current_dns', { adapter });
            currentDNS = result.servers || [];
            isDHCP = result.is_dhcp;
            
            const hasPublicDNS = currentDNS.some(dns => getProviderByIp(dns));
            netbooztDnsActive = hasPublicDNS && !isDHCP;
            
            // Inicializar métricas para DNS desconocidos
            for (const dns of currentDNS) {
                if (!metrics[dns]) {
                    metrics[dns] = {
                        ms: 0,
                        status: 'unknown',
                        protocol: 'UDP',
                        avgMs: 0,
                        checksCount: 0,
                        lastCheck: 0
                    };
                }
            }
        } catch (e) {
            console.error('Error cargando DNS:', e);
        } finally {
            loading = false;
        }
    }
    
    async function measureAllDNS() {
        testingLatency = true;
        lastLatencyCheck = Date.now();
        
        const allDNS = new Set<string>([
            ...DNS_PROVIDERS.flatMap(p => [p.primary, p.secondary]),
            ...currentDNS
        ]);
        
        // Marcar como testing
        for (const dns of allDNS) {
            if (metrics[dns]) metrics[dns].status = 'testing';
        }
        metrics = metrics;
        
        // Medir en paralelo
        const promises = Array.from(allDNS).map(async (dns) => {
            try {
                const result = await invoke<{ latency_ms: number; success: boolean }>('check_single_dns_health', { server: dns });
                const ms = result.success ? result.latency_ms : 999;
                
                if (metrics[dns]) {
                    // Actualizar promedio móvil
                    const oldCount = metrics[dns].checksCount;
                    const oldAvg = metrics[dns].avgMs;
                    const newCount = oldCount + 1;
                    const newAvg = oldCount === 0 ? ms : (oldAvg * oldCount + ms) / newCount;
                    
                    metrics[dns] = {
                        ...metrics[dns],
                        ms,
                        status: ms < 30 ? 'good' : ms < 80 ? 'warning' : 'bad',
                        avgMs: newAvg,
                        checksCount: newCount,
                        lastCheck: Date.now()
                    };
                }
            } catch {
                if (metrics[dns]) {
                    metrics[dns].ms = 999;
                    metrics[dns].status = 'bad';
                }
            }
        });
        
        await Promise.all(promises);
        metrics = metrics;
        testingLatency = false;
        saveMetricsHistory();
        
        if (autoFailoverEnabled && netbooztDnsActive) {
            autoReorderByLatency();
        }
    }
    
    function autoReorderByLatency() {
        const sorted = [...currentDNS].sort((a, b) => {
            const latA = metrics[a]?.ms ?? 999;
            const latB = metrics[b]?.ms ?? 999;
            return latA - latB;
        });
        
        if (JSON.stringify(sorted) !== JSON.stringify(currentDNS)) {
            dispatch('reorder', sorted);
        }
    }
    
    // ========== PROVIDERS ==========
    function getProviderByIp(ip: string): DnsProvider | null {
        return DNS_PROVIDERS.find(p => p.primary === ip || p.secondary === ip) || null;
    }
    
    function getProviderInfo(ip: string): { name: string; protocol: string; port: number; id?: string } {
        const provider = getProviderByIp(ip);
        if (provider) return { name: provider.name, protocol: provider.protocol, port: provider.port, id: provider.id };
        
        if (ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.')) {
            return { name: 'Router', protocol: 'UDP', port: 53 };
        }
        return { name: 'ISP', protocol: 'UDP', port: 53 };
    }
    
    // Verificar si es DNS personalizado por id
    function isCustomById(id?: string): boolean {
        return id?.startsWith('custom-') ?? false;
    }
    
    // Obtener DnsProvider completo por IP (para editar)
    function getFullProviderByIp(ip: string): DnsProvider | null {
        return DNS_PROVIDERS.find(p => p.primary === ip || p.secondary === ip) || null;
    }
    
    // ========== RECOMMENDATIONS ==========
    function getBestAvailableDNS(): DnsProvider | null {
        if (!DNS_PROVIDERS || DNS_PROVIDERS.length === 0) return null;
        const available = DNS_PROVIDERS.filter(p => !isDNSInUse(p.primary));
        if (available.length === 0) return null;
        
        let best: DnsProvider | null = null;
        let bestMs = Infinity;
        
        for (const p of available) {
            const m = metrics[p.primary];
            if (m && m.ms > 0 && m.ms < bestMs && m.status !== 'bad') {
                best = p;
                bestMs = m.ms;
            }
        }
        
        return best;
    }
    
    function isRecommended(provider: DnsProvider): boolean {
        if (currentDNS.length === 0) return false;
        
        const currentBestMs = Math.min(...currentDNS.map(dns => metrics[dns]?.ms ?? 999));
        const providerMs = metrics[provider.primary]?.ms ?? 999;
        
        // Recomendar si es 20% mejor que el mejor activo
        return providerMs > 0 && providerMs < currentBestMs * 0.8;
    }
    
    // ========== ACTIONS ==========
    async function activateDNS(provider: DnsProvider) {
        if (!adapter) return;
        loading = true;
        
        try {
            await invoke('set_dns_servers', { 
                adapter, 
                primary: provider.primary, 
                secondary: provider.secondary 
            });
            await loadCurrentDNS();
            netbooztDnsActive = true;
            saveState();
            
            dispatch('change', { dns: [provider.primary, provider.secondary], boosted: true });
            dispatch('showNotification', { 
                type: 'success', 
                message: `✓ DNS cambiado a ${provider.name}` 
            });
        } catch (e) {
            console.error('Error activando DNS:', e);
            dispatch('error', e);
        } finally {
            loading = false;
        }
    }
    
    async function deactivateDNS(ip: string) {
        // Quitar de la lista actual y reconfigurar
        const remaining = currentDNS.filter(dns => {
            const provider = getProviderByIp(dns);
            const targetProvider = getProviderByIp(ip);
            return !provider || !targetProvider || provider.id !== targetProvider.id;
        });
        
        if (remaining.length === 0) {
            await deactivateNetBooztDNS();
        } else {
            // Reconfigurar con los restantes
            loading = true;
            try {
                await invoke('set_dns_servers', { 
                    adapter, 
                    primary: remaining[0], 
                    secondary: remaining[1] || remaining[0] 
                });
                await loadCurrentDNS();
                saveState();
            } catch (e) {
                console.error('Error desactivando DNS:', e);
            } finally {
                loading = false;
            }
        }
    }
    
    async function activateNetBooztDNS() {
        if (!adapter) return;
        activatingBoostedDns = true;
        
        try {
            let bestDns = DNS_PROVIDERS[0];
            let bestLatency = 999;
            
            for (const dns of DNS_PROVIDERS) {
                const m = metrics[dns.primary];
                if (m && m.ms > 0 && m.ms < bestLatency && m.status !== 'bad') {
                    bestLatency = m.ms;
                    bestDns = dns;
                }
            }
            
            await invoke('set_dns_servers', { 
                adapter, 
                primary: bestDns.primary, 
                secondary: bestDns.secondary 
            });
            
            if (!autoFailoverEnabled) dispatch('toggleFailover');
            
            await loadCurrentDNS();
            netbooztDnsActive = true;
            saveState();
            
            dispatch('change', { dns: [bestDns.primary, bestDns.secondary], boosted: true });
            dispatch('showNotification', { 
                type: 'success', 
                message: `🚀 DNS Boosted: ${bestDns.name} (${bestLatency.toFixed(0)}ms)` 
            });
        } catch (e) {
            console.error('Error activando NetBoozt DNS:', e);
            dispatch('error', e);
        } finally {
            activatingBoostedDns = false;
        }
    }
    
    async function deactivateNetBooztDNS() {
        if (!adapter) return;
        activatingBoostedDns = true;
        
        try {
            await invoke('reset_dns_to_dhcp', { adapter });
            await loadCurrentDNS();
            netbooztDnsActive = false;
            saveState();
            dispatch('change', { dns: [], dhcp: true });
            dispatch('showNotification', { type: 'info', message: 'DNS reseteado a router' });
        } catch (e) {
            console.error('Error desactivando DNS:', e);
            dispatch('error', e);
        } finally {
            activatingBoostedDns = false;
        }
    }
    
    async function flushCache() {
        try {
            await invoke('flush_dns_cache');
            dispatch('flush');
            dispatch('showNotification', { type: 'success', message: '✓ Caché DNS limpiada' });
        } catch (e) {
            console.error('Error limpiando caché:', e);
        }
    }
    
    // ========== DRAG & DROP ==========
    function handleDragStart(e: DragEvent, dns: string) {
        if (!netbooztDnsActive) return;
        isDragging = true;
        draggedDns = dns;
        if (e.dataTransfer) {
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', dns);
        }
    }
    
    function handleDragOver(e: DragEvent, dns: string) {
        e.preventDefault();
        if (draggedDns && draggedDns !== dns) {
            dragOverTarget = dns;
        }
    }
    
    function handleDragLeave() {
        dragOverTarget = null;
    }
    
    async function handleDrop(e: DragEvent, targetDns: string) {
        e.preventDefault();
        
        if (!draggedDns || draggedDns === targetDns) {
            resetDragState();
            return;
        }
        
        // Reordenar
        const fromIndex = currentDNS.indexOf(draggedDns);
        const toIndex = currentDNS.indexOf(targetDns);
        
        if (fromIndex !== -1 && toIndex !== -1) {
            const newOrder = [...currentDNS];
            newOrder.splice(fromIndex, 1);
            newOrder.splice(toIndex, 0, draggedDns);
            
            // Aplicar nuevo orden
            loading = true;
            try {
                await invoke('set_dns_servers', { 
                    adapter, 
                    primary: newOrder[0], 
                    secondary: newOrder[1] || newOrder[0] 
                });
                currentDNS = newOrder;
                saveState();
                dispatch('reorder', newOrder);
            } catch (e) {
                console.error('Error reordenando DNS:', e);
            } finally {
                loading = false;
            }
        }
        
        resetDragState();
    }
    
    function handleDragEnd() {
        resetDragState();
    }
    
    function resetDragState() {
        isDragging = false;
        draggedDns = null;
        dragOverTarget = null;
    }
    
    // ========== HELPERS ==========
    function isDNSInUse(primary: string): boolean {
        return currentDNS.some(dns => {
            const p = getProviderByIp(dns);
            const target = getProviderByIp(primary);
            return p && target && p.id === target.id;
        });
    }
    
    function formatLatency(ms: number): string {
        if (ms === 0 || ms >= 999) return '--';
        return `${Math.round(ms)}`;
    }
    
    function getStatusColor(status: string): string {
        switch (status) {
            case 'good': return 'var(--success, #00ff88)';
            case 'warning': return 'var(--warning, #fdcb6e)';
            case 'bad': return 'var(--error, #ff6b6b)';
            default: return 'var(--text-muted, #666)';
        }
    }
    
    // Reactive
    $: activeDNSProviders = currentDNS.map(ip => ({ ip, provider: getProviderByIp(ip), info: getProviderInfo(ip), metrics: metrics[ip] }));
    $: availableProviders = (DNS_PROVIDERS || []).filter(p => !isDNSInUse(p.primary));
    $: recommendedDNS = getBestAvailableDNS();
</script>

<div class="dns-manager" class:compact>
    <!-- Header -->
    <div class="dns-header">
        <div class="header-title">
            <Icon name="globe" size={compact ? 16 : 18} />
            <h3>DNS</h3>
            {#if netbooztDnsActive}
                <span class="mode-badge boosted">🚀 Boosted</span>
            {:else if isDHCP}
                <span class="mode-badge dhcp">Router</span>
            {:else}
                <span class="mode-badge static">Manual</span>
            {/if}
        </div>
        <div class="header-actions">
            <!-- Botón para agregar DNS personalizado -->
            <button class="icon-btn add-dns-btn" on:click={openAddDnsModal} title="Agregar DNS Personalizado">
                <Icon name="plus" size={14} />
            </button>
            <!-- Botón de configuración recomendada con pulse -->
            {#if !netbooztDnsActive && isDHCP}
                <button 
                    class="icon-btn recommended pulse-btn" 
                    on:click={activateNetBooztDNS} 
                    disabled={loading || activatingBoostedDns || testingLatency}
                    title="Activar DNS Recomendado"
                >
                    <span class="pulse-ring"></span>
                    <span class="pulse-ring delay"></span>
                    <Icon name="zap" size={14} />
                </button>
            {/if}
            {#if netbooztDnsActive || !isDHCP}
                <button class="icon-btn" on:click={deactivateNetBooztDNS} disabled={loading || activatingBoostedDns} title="Volver a Router">
                    <Icon name="home" size={14} />
                </button>
            {/if}
            <button class="icon-btn" on:click={flushCache} disabled={loading} title="Limpiar Caché">
                <Icon name="trash-2" size={14} />
            </button>
            <button class="icon-btn" on:click={measureAllDNS} disabled={testingLatency} title="Medir Latencias">
                <Icon name="activity" size={14} className={testingLatency ? 'spinning' : ''} />
            </button>
        </div>
    </div>
    
    <div class="dns-content">
        {#if loading && currentDNS.length === 0}
            <div class="loading-state">
                <span class="spinner"></span>
                Cargando configuración DNS...
            </div>
        {:else if isDHCP && !netbooztDnsActive}
            <!-- Estado: Router/DHCP -->
            <div class="status-card router">
                <div class="status-icon">🏠</div>
                <div class="status-info">
                    <span class="status-title">DNS del Router</span>
                    <span class="status-desc">Resolución DNS manejada por tu ISP</span>
                </div>
            </div>
            
            <div class="boost-cta">
                <p>💡 Activa <strong>DNS Boosted</strong> para mejor velocidad</p>
                <button class="btn-boost" on:click={activateNetBooztDNS} disabled={activatingBoostedDns || testingLatency}>
                    {#if activatingBoostedDns}
                        <span class="spinner-sm"></span> Configurando...
                    {:else}
                        🚀 Activar DNS Boosted
                    {/if}
                </button>
            </div>
            
            <!-- Preview de servidores disponibles -->
            <div class="preview-section">
                <h4><Icon name="server" size={12} /> Servidores Disponibles</h4>
                <div class="dns-table">
                    <div class="table-header">
                        <span class="col-name">Servidor</span>
                        <span class="col-ip">IP</span>
                        <span class="col-latency">ms</span>
                        <span class="col-protocol">Protocolo</span>
                        <span class="col-action"></span>
                    </div>
                    {#each DNS_PROVIDERS.slice(0, 4) as provider}
                        {@const m = metrics[provider.primary] || { ms: 0, status: 'unknown' }}
                        <div class="table-row">
                            <span class="col-name">{provider.name}</span>
                            <span class="col-ip mono">{provider.primary}</span>
                            <span class="col-latency" style="color: {getStatusColor(m.status)}">
                                {#if m.status === 'testing'}
                                    <span class="spinner-xs"></span>
                                {:else}
                                    {formatLatency(m.ms)}
                                {/if}
                            </span>
                            <span class="col-protocol">{provider.protocol}</span>
                            <button class="btn-sm" on:click={() => activateDNS(provider)} disabled={loading}>
                                <Icon name="plus" size={12} />
                            </button>
                        </div>
                    {/each}
                </div>
            </div>
        {:else}
            <!-- Estado: Boosted Activo o Manual -->
            <div class="status-card boosted">
                <div class="status-icon">🚀</div>
                <div class="status-info">
                    <span class="status-title">DNS Boosted Activo</span>
                    <span class="status-desc">Auto-failover {autoFailoverEnabled ? 'habilitado' : 'deshabilitado'}</span>
                </div>
            </div>
            
            <!-- Tabla: DNS En Uso -->
            <div class="dns-section">
                <div class="section-header active">
                    <Icon name="check-circle" size={12} />
                    <span>En Uso</span>
                    <span class="count">{currentDNS.length}</span>
                </div>
                
                <div class="dns-table">
                    <div class="table-header">
                        <span class="col-rank">#</span>
                        <span class="col-name">Servidor</span>
                        <span class="col-ip">IP</span>
                        <span class="col-latency">ms</span>
                        <span class="col-avg">Prom.</span>
                        <span class="col-protocol">Puerto</span>
                        <span class="col-action"></span>
                    </div>
                    
                    {#each activeDNSProviders as { ip, provider, info, metrics: m }, index}
                        {@const isCustom = isCustomById(info.id)}
                        {@const fullProvider = getFullProviderByIp(ip)}
                        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
                        <div 
                            class="table-row active"
                            class:primary={index === 0}
                            class:custom={isCustom}
                            class:dragging={draggedDns === ip}
                            class:drag-over={dragOverTarget === ip}
                            role="listitem"
                            draggable={netbooztDnsActive}
                            on:dragstart={(e) => handleDragStart(e, ip)}
                            on:dragover={(e) => handleDragOver(e, ip)}
                            on:dragleave={handleDragLeave}
                            on:drop={(e) => handleDrop(e, ip)}
                            on:dragend={handleDragEnd}
                        >
                            <span class="col-rank">
                                <span class="rank-num">{index + 1}</span>
                                {#if netbooztDnsActive}
                                    <Icon name="grip-vertical" size={10} className="drag-handle" />
                                {/if}
                            </span>
                            <span class="col-name">
                                {info.name}
                                {#if isCustom}
                                    <span class="custom-badge">CUSTOM</span>
                                {/if}
                            </span>
                            <span class="col-ip mono">{ip}</span>
                            <span class="col-latency" style="color: {getStatusColor(m?.status || 'unknown')}">
                                {#if m?.status === 'testing'}
                                    <span class="spinner-xs"></span>
                                {:else}
                                    {formatLatency(m?.ms || 0)}
                                {/if}
                            </span>
                            <span class="col-avg mono" title="Promedio de {m?.checksCount || 0} mediciones. Calculado usando media móvil exponencial de las últimas latencias registradas.">
                                {m?.checksCount > 0 ? `~${Math.round(m.avgMs)}` : '--'}
                            </span>
                            <span class="col-protocol" title="Puerto {info.port}: Puerto estándar DNS ({info.port === 53 ? 'UDP/TCP' : info.port === 443 ? 'HTTPS/DoH' : 'Alternativo'}). Protocolo: {info.protocol || 'UDP'}">:{info.port}</span>
                            <span class="col-action" style="display: flex; gap: 0.2rem;">
                                {#if isCustom && fullProvider}
                                    <button class="btn-edit" on:click|stopPropagation={() => openEditDnsModal(fullProvider)} title="Editar">
                                        <Icon name="edit-2" size={10} />
                                    </button>
                                {/if}
                                <button class="btn-remove" on:click={() => deactivateDNS(ip)} disabled={loading} title="Quitar">
                                    <Icon name="x" size={12} />
                                </button>
                            </span>
                        </div>
                    {/each}
                </div>
            </div>
            
            <!-- Separador -->
            <div class="section-divider">
                <span class="divider-line"></span>
                <span class="divider-text">disponibles</span>
                <span class="divider-line"></span>
            </div>
            
            <!-- Tabla: DNS Disponibles -->
            <div class="dns-section">
                <div class="section-header available">
                    <Icon name="layers" size={12} />
                    <span>Disponibles</span>
                    {#if recommendedDNS}
                        <span class="recommended-badge">★ Mejor opción disponible</span>
                    {/if}
                </div>
                
                {#if availableProviders.length > 0}
                    <div class="dns-table">
                        <div class="table-header">
                            <span class="col-name">Servidor</span>
                            <span class="col-ip">IP</span>
                            <span class="col-latency">ms</span>
                            <span class="col-avg">Prom.</span>
                            <span class="col-protocol">Puerto</span>
                            <span class="col-action"></span>
                        </div>
                        
                        {#each availableProviders as provider}
                            {@const m = metrics[provider.primary] || { ms: 0, status: 'unknown', avgMs: 0, checksCount: 0 }}
                            {@const isRec = isRecommended(provider)}
                            {@const isCustom = isCustomDns(provider)}
                            <div 
                                class="table-row available"
                                class:recommended={isRec}
                                class:custom={isCustom}
                            >
                                <span class="col-name">
                                    {provider.name}
                                    {#if isRec}
                                        <span class="rec-star">★</span>
                                    {/if}
                                    {#if isCustom}
                                        <span class="custom-badge">CUSTOM</span>
                                    {/if}
                                </span>
                                <span class="col-ip mono">{provider.primary}</span>
                                <span class="col-latency" style="color: {getStatusColor(m.status)}">
                                    {#if m.status === 'testing'}
                                        <span class="spinner-xs"></span>
                                    {:else}
                                        {formatLatency(m.ms)}
                                    {/if}
                                </span>
                                <span class="col-avg mono">
                                    {m.checksCount > 0 ? `~${Math.round(m.avgMs)}` : '--'}
                                </span>
                                <span class="col-protocol">:{provider.port}</span>
                                <span class="col-action" style="display: flex; gap: 0.25rem;">
                                    {#if isCustom}
                                        <button class="btn-edit" on:click|stopPropagation={() => openEditDnsModal(provider)} title="Editar">
                                            <Icon name="edit-2" size={10} />
                                        </button>
                                    {/if}
                                    <button class="btn-sm" on:click={() => activateDNS(provider)} disabled={loading} title="Activar">
                                        <Icon name="plus" size={12} />
                                    </button>
                                </span>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="all-active-msg">
                        <Icon name="check-circle" size={14} />
                        Todos los servidores están activos
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

<!-- Modal para agregar/editar DNS -->
{#if showDnsModal}
    <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
    <div class="modal-overlay" on:click={() => showDnsModal = false}>
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <div 
            class="modal-content" 
            role="dialog" 
            aria-modal="true"
            aria-labelledby="dns-modal-title"
            on:click|stopPropagation 
            on:keydown={(e) => e.key === 'Escape' && (showDnsModal = false)}
        >
            <div class="modal-header">
                <h3 id="dns-modal-title">
                    <Icon name={editingDns ? 'edit-2' : 'plus-circle'} size={16} />
                    {editingDns ? 'Editar DNS' : 'Agregar DNS Personalizado'}
                </h3>
                <button class="modal-close" on:click={() => showDnsModal = false} aria-label="Cerrar modal">
                    <Icon name="x" size={16} />
                </button>
            </div>
            
            <div class="modal-body">
                <div class="form-group">
                    <label for="dns-name">Nombre del servidor</label>
                    <input 
                        type="text" 
                        id="dns-name" 
                        bind:value={dnsForm.name}
                        placeholder="Ej: Mi DNS, Trabajo, ISP..."
                        maxlength="30"
                    />
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="dns-primary">IP Primaria *</label>
                        <input 
                            type="text" 
                            id="dns-primary" 
                            bind:value={dnsForm.primary}
                            placeholder="Ej: 192.168.1.1"
                            class="mono"
                        />
                    </div>
                    <div class="form-group">
                        <label for="dns-secondary">IP Secundaria</label>
                        <input 
                            type="text" 
                            id="dns-secondary" 
                            bind:value={dnsForm.secondary}
                            placeholder="Opcional"
                            class="mono"
                        />
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="dns-protocol">Protocolo</label>
                        <select id="dns-protocol" bind:value={dnsForm.protocol}>
                            <option value="UDP">UDP (estándar)</option>
                            <option value="TCP">TCP</option>
                            <option value="DoH">DoH (HTTPS)</option>
                            <option value="DoT">DoT (TLS)</option>
                            <option value="DNSCrypt">DNSCrypt</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="dns-port">Puerto</label>
                        <input 
                            type="number" 
                            id="dns-port" 
                            bind:value={dnsForm.port}
                            min="1"
                            max="65535"
                        />
                    </div>
                </div>
                
                {#if dnsFormError}
                    <div class="form-error">
                        <Icon name="alert-triangle" size={12} />
                        {dnsFormError}
                    </div>
                {/if}
            </div>
            
            <div class="modal-footer">
                {#if editingDns}
                    <button class="btn-delete" on:click={() => { if (editingDns) deleteCustomDns(editingDns); showDnsModal = false; }}>
                        <Icon name="trash-2" size={14} />
                        Eliminar
                    </button>
                {/if}
                <button class="btn-secondary" on:click={() => showDnsModal = false}>Cancelar</button>
                <button class="btn-primary" on:click={saveDnsForm}>
                    <Icon name="check" size={14} />
                    {editingDns ? 'Guardar' : 'Agregar'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    .dns-manager {
        display: flex;
        flex-direction: column;
        height: 100%;
        gap: 0.5rem;
    }
    
    /* Header */
    .dns-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .header-title h3 {
        margin: 0;
        font-size: 0.9375rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .mode-badge {
        font-size: 0.5625rem;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    .mode-badge.dhcp { background: rgba(253, 203, 110, 0.15); color: var(--warning, #fdcb6e); }
    .mode-badge.boosted { background: rgba(0, 212, 170, 0.15); color: var(--primary, #00d4aa); }
    .mode-badge.static { background: rgba(100, 100, 255, 0.15); color: #6b7cff; }
    
    .header-actions {
        display: flex;
        gap: 0.35rem;
    }
    
    .icon-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 5px;
        color: var(--text-muted, #888);
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .icon-btn:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }
    
    /* Botón con efecto pulse para recomendación */
    .icon-btn.pulse-btn {
        position: relative;
        overflow: visible;
        background: rgba(0, 212, 170, 0.2);
        border-color: rgba(0, 212, 170, 0.5);
        color: var(--primary, #00d4aa);
    }
    
    .icon-btn.pulse-btn .pulse-ring {
        position: absolute;
        inset: -4px;
        border-radius: 8px;
        border: 2px solid rgba(0, 212, 170, 0.5);
        animation: pulseRing 2s ease-out infinite;
        pointer-events: none;
    }
    
    .icon-btn.pulse-btn .pulse-ring.delay {
        animation-delay: 1s;
    }
    
    @keyframes pulseRing {
        0% {
            transform: scale(1);
            opacity: 0.8;
        }
        100% {
            transform: scale(1.6);
            opacity: 0;
        }
    }
    
    .icon-btn.pulse-btn:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    .icon-btn.pulse-btn:hover .pulse-ring {
        animation: none;
        opacity: 0;
    }
    
    :global(.spinning) { animation: spin 1s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    /* Content */
    .dns-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        overflow-y: auto;
    }
    
    .loading-state {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 2rem;
        color: var(--text-muted, #666);
    }
    
    .spinner {
        width: 18px;
        height: 18px;
        border: 2px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .spinner-sm {
        width: 14px;
        height: 14px;
        border: 2px solid rgba(0,0,0,0.2);
        border-top-color: #000;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .spinner-xs {
        display: inline-block;
        width: 10px;
        height: 10px;
        border: 1.5px solid var(--border, #3d3d3d);
        border-top-color: var(--text-muted, #888);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    /* Status Cards */
    .status-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
    }
    
    .status-card.router {
        background: rgba(253, 203, 110, 0.08);
        border: 1px solid rgba(253, 203, 110, 0.2);
    }
    
    .status-card.boosted {
        background: rgba(0, 212, 170, 0.08);
        border: 1px solid rgba(0, 212, 170, 0.25);
    }
    
    .status-icon { font-size: 1.25rem; }
    .status-info { display: flex; flex-direction: column; gap: 0.1rem; }
    .status-title { font-size: 0.8125rem; font-weight: 600; color: var(--text-primary, #fff); }
    .status-desc { font-size: 0.6875rem; color: var(--text-muted, #666); }
    
    /* Boost CTA */
    .boost-cta {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem;
        background: rgba(0, 212, 170, 0.05);
        border: 1px dashed rgba(0, 212, 170, 0.25);
        border-radius: 8px;
        text-align: center;
    }
    
    .boost-cta p {
        margin: 0;
        font-size: 0.8125rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .boost-cta strong { color: var(--primary, #00d4aa); }
    
    .btn-boost {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        font-size: 0.8125rem;
        font-weight: 600;
        background: linear-gradient(135deg, var(--primary, #00d4aa), #00b894);
        color: #000;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-boost:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3); }
    .btn-boost:disabled { opacity: 0.6; cursor: not-allowed; }
    
    /* Preview Section */
    .preview-section h4 {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        margin: 0 0 0.5rem 0;
        font-size: 0.6875rem;
        font-weight: 600;
        color: var(--text-muted, #888);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    /* DNS Section */
    .dns-section {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.5rem;
        font-size: 0.625rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        border-radius: 4px;
    }
    
    .section-header.active { color: var(--primary, #00d4aa); background: rgba(0, 212, 170, 0.1); }
    .section-header.available { color: var(--text-muted, #666); }
    
    .section-header .count {
        margin-left: auto;
        background: rgba(255,255,255,0.1);
        padding: 0.1rem 0.35rem;
        border-radius: 8px;
        font-size: 0.5625rem;
    }
    
    .recommended-badge {
        margin-left: auto;
        color: var(--warning, #fdcb6e);
        font-size: 0.5625rem;
        font-weight: 600;
    }
    
    /* DNS Table */
    .dns-table {
        display: flex;
        flex-direction: column;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 6px;
        border: 1px solid var(--border, #3d3d3d);
        overflow: hidden;
    }
    
    .table-header {
        display: grid;
        grid-template-columns: 2.5rem 1fr 6.5rem 2.5rem 2.5rem 3rem 1.75rem;
        gap: 0.25rem;
        padding: 0.35rem 0.5rem;
        background: rgba(255,255,255,0.03);
        border-bottom: 1px solid var(--border, #3d3d3d);
        font-size: 0.5625rem;
        font-weight: 600;
        color: var(--text-muted, #666);
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .table-row {
        display: grid;
        grid-template-columns: 2.5rem 1fr 6.5rem 2.5rem 2.5rem 3rem 1.75rem;
        gap: 0.25rem;
        padding: 0.4rem 0.5rem;
        align-items: center;
        font-size: 0.75rem;
        border-bottom: 1px solid rgba(255,255,255,0.03);
        transition: background 0.1s;
    }
    
    .table-row:last-child { border-bottom: none; }
    
    .table-row.active { background: rgba(0, 212, 170, 0.05); }
    .table-row.active.primary { background: rgba(0, 212, 170, 0.1); border-left: 2px solid var(--primary, #00d4aa); }
    .table-row.active:hover { background: rgba(0, 212, 170, 0.12); }
    
    .table-row.available {
        cursor: pointer;
        border: none;
        width: 100%;
        text-align: left;
        font-family: inherit;
        background: transparent;
    }
    
    .table-row.available:hover:not(:disabled) { background: rgba(0, 212, 170, 0.08); }
    .table-row.available:disabled { opacity: 0.4; cursor: not-allowed; }
    
    .table-row.recommended { background: rgba(253, 203, 110, 0.08); }
    .table-row.recommended:hover { background: rgba(253, 203, 110, 0.12); }
    
    .table-row.dragging { opacity: 0.5; background: var(--primary, #00d4aa); }
    .table-row.drag-over { background: rgba(0, 212, 170, 0.2); border-top: 2px solid var(--primary, #00d4aa); }
    
    .col-rank {
        display: flex;
        align-items: center;
        gap: 0.15rem;
    }
    
    .rank-num {
        font-size: 0.625rem;
        font-weight: 700;
        color: var(--text-muted, #666);
        min-width: 12px;
    }
    
    .table-row.active.primary .rank-num { color: var(--primary, #00d4aa); }
    
    :global(.drag-handle) {
        opacity: 0.3;
        cursor: grab;
        transition: opacity 0.15s;
    }
    
    .table-row:hover :global(.drag-handle) { opacity: 0.7; }
    
    .col-name {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-weight: 500;
        color: var(--text-primary, #fff);
    }
    
    .rec-star { color: var(--warning, #fdcb6e); font-size: 0.625rem; }
    
    .col-ip { color: var(--text-muted, #888); }
    .col-latency { font-weight: 600; text-align: center; }
    .col-avg { font-size: 0.625rem; color: var(--text-muted, #666); text-align: center; }
    .col-protocol { font-size: 0.625rem; color: var(--text-muted, #666); }
    .col-action { display: flex; justify-content: center; }
    
    .mono { font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.6875rem; }
    
    .btn-sm {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        color: #fff;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .btn-sm:hover:not(:disabled) { 
        transform: scale(1.1); 
        background: var(--primary, #00d4aa);
        border-color: var(--primary, #00d4aa);
        color: #000;
    }
    .btn-sm:disabled { opacity: 0.4; cursor: not-allowed; }
    
    .btn-remove {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        background: transparent;
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 4px;
        color: var(--error, #ff6b6b);
        cursor: pointer;
        opacity: 0;
        transition: all 0.15s;
    }
    
    .table-row:hover .btn-remove { opacity: 1; }
    .btn-remove:hover { background: rgba(255, 107, 107, 0.15); }
    .btn-remove:disabled { opacity: 0.3; cursor: not-allowed; }
    
    /* Section Divider */
    .section-divider {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0;
    }
    
    .divider-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border, #3d3d3d), transparent);
    }
    
    .divider-text {
        font-size: 0.5625rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted, #666);
        padding: 0.1rem 0.5rem;
        background: var(--bg-card, #1a1a1a);
        border-radius: 8px;
    }
    
    .all-active-msg {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 1rem;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    /* Botón agregar DNS */
    .add-dns-btn {
        background: rgba(0, 212, 170, 0.15);
        border-color: rgba(0, 212, 170, 0.3);
        color: var(--primary, #00d4aa);
    }
    
    .add-dns-btn:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    /* Modal de DNS */
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.15s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .modal-content {
        width: 90%;
        max-width: 400px;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        animation: slideUp 0.2s ease;
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid var(--border, #3d3d3d);
    }
    
    .modal-header h3 {
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .modal-close {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: transparent;
        border: none;
        color: var(--text-muted, #888);
        cursor: pointer;
        border-radius: 6px;
        transition: all 0.15s;
    }
    
    .modal-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary, #fff);
    }
    
    .modal-body {
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
    }
    
    .form-group label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted, #888);
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    .form-group input,
    .form-group select {
        padding: 0.6rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-primary, #fff);
        font-size: 0.875rem;
        transition: border-color 0.15s;
    }
    
    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: var(--primary, #00d4aa);
    }
    
    .form-group input::placeholder {
        color: var(--text-muted, #666);
    }
    
    .form-group input.mono {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
    }
    
    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }
    
    .form-error {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 6px;
        color: var(--error, #ff6b6b);
        font-size: 0.75rem;
    }
    
    .modal-footer {
        display: flex;
        justify-content: flex-end;
        gap: 0.5rem;
        padding: 1rem 1.25rem;
        border-top: 1px solid var(--border, #3d3d3d);
        background: rgba(255, 255, 255, 0.02);
    }
    
    .btn-primary,
    .btn-secondary,
    .btn-delete {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.5rem 1rem;
        font-size: 0.8125rem;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary, #00d4aa), #00b894);
        color: #000;
    }
    
    .btn-primary:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
    }
    
    .btn-secondary {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-secondary, #a0a0a0);
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .btn-secondary:hover {
        background: var(--border, #3d3d3d);
        color: var(--text-primary, #fff);
    }
    
    .btn-delete {
        background: transparent;
        color: var(--error, #ff6b6b);
        border: 1px solid rgba(255, 107, 107, 0.3);
        margin-right: auto;
    }
    
    .btn-delete:hover {
        background: rgba(255, 107, 107, 0.15);
    }
    
    /* Badge para DNS custom */
    .custom-badge {
        font-size: 0.5rem;
        padding: 0.1rem 0.3rem;
        background: rgba(100, 100, 255, 0.15);
        color: #6b7cff;
        border-radius: 3px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Botón de editar (solo visible en custom) */
    .btn-edit {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        background: transparent;
        border: 1px solid rgba(100, 124, 255, 0.3);
        border-radius: 4px;
        color: #6b7cff;
        cursor: pointer;
        opacity: 0;
        transition: all 0.15s;
    }
    
    .table-row:hover .btn-edit { opacity: 1; }
    .btn-edit:hover { background: rgba(100, 124, 255, 0.15); }
</style>
