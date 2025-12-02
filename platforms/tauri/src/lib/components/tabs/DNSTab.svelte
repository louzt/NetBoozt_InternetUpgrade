<!--
    DNSTab.svelte - Tab modular de DNS
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import DNSCard from '../DNSCard.svelte';
    import SkeletonCard from '../SkeletonCard.svelte';
    
    export let loading = false;
    export let currentDNS: string[] = [];
    export let currentTier = 1;
    export let dnsHealthMap: Record<string, any> = {};
    export let settingDNS = false;
    export let autoFailoverEnabled = false;
    
    const dispatch = createEventDispatcher();
    
    const dnsProviders = [
        { id: 'cloudflare', name: 'Cloudflare', primary: '1.1.1.1', secondary: '1.0.0.1', tier: 1, description: 'El DNS más rápido', features: ['Rápido', 'Privacidad', 'Sin logs'] },
        { id: 'google', name: 'Google', primary: '8.8.8.8', secondary: '8.8.4.4', tier: 2, description: 'DNS público de Google', features: ['Confiable', 'Global', 'Anycast'] },
        { id: 'quad9', name: 'Quad9', primary: '9.9.9.9', secondary: '149.112.112.112', tier: 3, description: 'Con bloqueo de malware', features: ['Seguridad', 'Privacidad'] },
        { id: 'opendns', name: 'OpenDNS', primary: '208.67.222.222', secondary: '208.67.220.220', tier: 4, description: 'DNS con filtrado', features: ['Filtrado', 'Control parental'] },
        { id: 'adguard', name: 'AdGuard', primary: '94.140.14.14', secondary: '94.140.15.15', tier: 5, description: 'Bloqueo de anuncios', features: ['Ad-blocking', 'Trackers'] },
        { id: 'cleanbrowsing', name: 'CleanBrowsing', primary: '185.228.168.9', secondary: '185.228.169.9', tier: 6, description: 'DNS familiar', features: ['Familia', 'Seguro'] }
    ];
</script>

<div class="dns-page">
    <section class="card">
        <div class="card-header">
            <h2>🌐 DNS Actual</h2>
            <div class="failover-toggle">
                <label class="toggle">
                    <input type="checkbox" checked={autoFailoverEnabled} on:change={() => dispatch('toggleFailover')} />
                    <span class="toggle-slider"></span>
                </label>
                <span>Auto-Failover</span>
            </div>
        </div>
        
        <div class="current-dns-display">
            {#if currentDNS.length > 0}
                <div class="dns-current-item"><span class="dns-label">Primario:</span><span class="dns-value">{currentDNS[0]}</span></div>
                {#if currentDNS[1]}<div class="dns-current-item"><span class="dns-label">Secundario:</span><span class="dns-value">{currentDNS[1]}</span></div>{/if}
                <div class="tier-badge">Tier {currentTier}</div>
            {:else}
                <p class="text-muted">Usando DNS del DHCP (automático)</p>
            {/if}
        </div>
    </section>
    
    <section class="card">
        <h2>📋 Servidores DNS Disponibles</h2>
        <p class="card-desc">Selecciona un servidor para mejorar velocidad y privacidad</p>
        
        <div class="dns-grid">
            {#if loading}
                {#each [1,2,3,4,5,6] as _}
                    <SkeletonCard variant="dns" />
                {/each}
            {:else}
                {#each dnsProviders as provider}
                    <DNSCard 
                        name={provider.name}
                        primary={provider.primary}
                        secondary={provider.secondary}
                        tier={provider.tier}
                        description={provider.description}
                        features={provider.features}
                        selected={currentDNS[0] === provider.primary}
                        health={dnsHealthMap[provider.primary] || null}
                        loading={settingDNS}
                        onSelect={() => dispatch('setDNS', provider)}
                    />
                {/each}
            {/if}
        </div>
        
        <div class="dns-actions">
            <button class="btn btn-secondary" on:click={() => dispatch('resetDNS')} disabled={settingDNS}>🔄 Resetear a DHCP</button>
            <button class="btn btn-ghost" on:click={() => dispatch('flushDNS')}>🧹 Limpiar Caché</button>
        </div>
    </section>
</div>

<style>
    .dns-page { display: flex; flex-direction: column; gap: 1.5rem; }
    .card { background: var(--bg-card, #1a1a1a); border-radius: 12px; padding: 1.25rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-primary, #fff); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .card-header h2 { margin-bottom: 0; }
    .card-desc { font-size: 0.875rem; color: var(--text-secondary, #a0a0a0); margin-bottom: 1rem; }
    .dns-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .current-dns-display { display: flex; flex-wrap: wrap; align-items: center; gap: 1rem; padding: 1rem; background: var(--bg-elevated, #2b2b2b); border-radius: 8px; }
    .dns-current-item { display: flex; align-items: center; gap: 0.5rem; }
    .dns-label { font-size: 0.75rem; color: var(--text-muted, #666); }
    .dns-value { font-family: monospace; font-size: 0.875rem; color: var(--primary, #00d4aa); }
    .tier-badge { background: var(--primary, #00d4aa); color: #000; font-size: 0.7rem; font-weight: 700; padding: 0.25rem 0.75rem; border-radius: 20px; }
    .dns-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
    .failover-toggle { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: var(--text-secondary, #a0a0a0); }
    .toggle { position: relative; width: 44px; height: 24px; }
    .toggle input { opacity: 0; width: 0; height: 0; }
    .toggle-slider { position: absolute; cursor: pointer; inset: 0; background: var(--bg-elevated, #2b2b2b); border-radius: 24px; transition: 0.3s; }
    .toggle-slider::before { content: ''; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px; background: var(--text-muted, #666); border-radius: 50%; transition: 0.3s; }
    .toggle input:checked + .toggle-slider { background: rgba(0, 212, 170, 0.3); }
    .toggle input:checked + .toggle-slider::before { transform: translateX(20px); background: var(--primary, #00d4aa); }
    .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: all 0.15s; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-secondary { background: var(--bg-elevated, #2b2b2b); color: var(--text-primary, #fff); }
    .btn-secondary:hover:not(:disabled) { background: #3b3b3b; }
    .btn-ghost { background: transparent; color: var(--text-secondary, #a0a0a0); }
    .btn-ghost:hover:not(:disabled) { background: var(--bg-elevated, #2b2b2b); }
    .text-muted { color: var(--text-muted, #666); }
</style>
