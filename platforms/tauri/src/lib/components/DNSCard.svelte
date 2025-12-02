<script lang="ts">
    /**
     * NetBoozt - DNS Card Component
     * Tarjeta de servidor DNS seleccionable
     * 
     * By LOUST (www.loust.pro)
     */
    
    import type { DNSHealth } from '$lib/types';
    import DNSIcon from './DNSIcon.svelte';
    
    export let name: string;
    export let primary: string;
    export let secondary: string = '';
    export let tier: number = 1;
    export let description: string = '';
    export let features: string[] = [];
    export let selected: boolean = false;
    export let health: DNSHealth | null = null;
    export let loading: boolean = false;
    export let onSelect: () => void = () => {};
    
    // Detectar provider ID basado en nombre
    $: providerId = name.toLowerCase().replace(/\s+/g, '');
    
    $: statusColor = health?.status === 'up' ? 'var(--success)' :
                     health?.status === 'slow' ? 'var(--warning)' :
                     health?.status === 'down' ? 'var(--error)' : 'var(--text-muted)';
                     
    $: statusText = health?.status === 'up' ? 'Online' :
                    health?.status === 'slow' ? 'Lento' :
                    health?.status === 'down' ? 'Offline' : 'Desconocido';
</script>

<button 
    class="dns-card" 
    class:selected
    class:loading
    on:click={onSelect}
    disabled={loading}
>
    <div class="dns-header">
        <DNSIcon provider={providerId} size={36} />
        <span class="dns-tier">Tier {tier}</span>
    </div>
    
    <h3 class="dns-name">{name}</h3>
    
    <div class="dns-servers">
        <span class="dns-ip">{primary}</span>
        {#if secondary && secondary !== 'auto'}
            <span class="dns-ip secondary">{secondary}</span>
        {/if}
    </div>
    
    {#if description}
        <p class="dns-description">{description}</p>
    {/if}
    
    {#if features.length > 0}
        <div class="dns-features">
            {#each features as feature}
                <span class="feature-tag">{feature}</span>
            {/each}
        </div>
    {/if}
    
    {#if health}
        <div class="dns-health">
            <div class="health-indicator" style="--status-color: {statusColor}">
                <span class="health-dot"></span>
                <span class="health-text">{statusText}</span>
            </div>
            {#if health.latency_ms > 0}
                <span class="health-latency">{health.latency_ms.toFixed(0)}ms</span>
            {/if}
        </div>
    {/if}
    
    {#if loading}
        <div class="dns-loading">
            <div class="spinner-small"></div>
        </div>
    {/if}
</button>

<style>
    .dns-card {
        display: flex;
        flex-direction: column;
        align-items: stretch;
        gap: 0.5rem;
        padding: 1rem;
        background: var(--bg-elevated, #333);
        border-radius: 12px;
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    .dns-card:hover:not(:disabled) {
        border-color: var(--primary, #00d4aa);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 212, 170, 0.15);
    }
    
    .dns-card.selected {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.1);
    }
    
    .dns-card:disabled {
        cursor: not-allowed;
        opacity: 0.7;
    }
    
    .dns-card.loading::after {
        content: '';
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.3);
    }
    
    .dns-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    
    .dns-tier {
        font-size: 0.65rem;
        color: var(--text-muted, #888);
        background: var(--bg-card, #2b2b2b);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    .dns-name {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0.25rem 0;
    }
    
    .dns-servers {
        display: flex;
        flex-direction: column;
        gap: 0.125rem;
    }
    
    .dns-ip {
        font-size: 0.75rem;
        font-family: 'JetBrains Mono', 'Consolas', monospace;
        color: var(--primary, #00d4aa);
    }
    
    .dns-ip.secondary {
        color: var(--text-muted, #888);
    }
    
    .dns-description {
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
        margin: 0;
        line-height: 1.4;
    }
    
    .dns-features {
        display: flex;
        flex-wrap: wrap;
        gap: 0.25rem;
        margin-top: 0.25rem;
    }
    
    .feature-tag {
        font-size: 0.6rem;
        color: var(--text-muted, #888);
        background: var(--bg-card, #2b2b2b);
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
    }
    
    .dns-health {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .health-indicator {
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }
    
    .health-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--status-color);
        animation: pulse 2s infinite;
    }
    
    .health-text {
        font-size: 0.65rem;
        color: var(--status-color);
        font-weight: 500;
    }
    
    .health-latency {
        font-size: 0.65rem;
        color: var(--text-muted, #888);
        font-family: monospace;
    }
    
    .dns-loading {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
    }
    
    .spinner-small {
        width: 24px;
        height: 24px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
