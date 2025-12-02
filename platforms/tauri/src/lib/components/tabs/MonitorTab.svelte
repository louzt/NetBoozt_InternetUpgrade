<!--
    MonitorTab.svelte - Tab de Monitor en Tiempo Real
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import StatCard from '../StatCard.svelte';
    import SkeletonCard from '../SkeletonCard.svelte';
    
    export let loading = false;
    export let monitoringActive = false;
    export let downloadRate = 0;
    export let uploadRate = 0;
    export let latency = 0;
    export let packetsSent = 0;
    export let packetsRecv = 0;
    export let totalErrors = 0;
    export let totalDrops = 0;
    
    const dispatch = createEventDispatcher();
</script>

<div class="monitor-page">
    <section class="card">
        <div class="card-header">
            <h2>📈 Monitor en Tiempo Real</h2>
            <button class="btn {monitoringActive ? 'btn-danger' : 'btn-primary'}" on:click={() => dispatch('toggle')}>
                {monitoringActive ? '⏹️ Detener' : '▶️ Iniciar'} Monitoreo
            </button>
        </div>
        
        <div class="monitor-stats">
            {#if loading}
                {#each [1,2,3,4,5,6] as _}
                    <SkeletonCard variant="stat" />
                {/each}
            {:else}
                <StatCard icon="📥" label="Descarga" value={downloadRate.toFixed(2)} unit="Mbps" variant="primary" />
                <StatCard icon="📤" label="Subida" value={uploadRate.toFixed(2)} unit="Mbps" variant="success" />
                <StatCard icon="🏓" label="Latencia" value={latency.toFixed(0)} unit="ms" variant={latency > 100 ? 'warning' : 'default'} />
                <StatCard icon="📦" label="Paquetes/s" value={(packetsSent + packetsRecv).toFixed(0)} unit="" />
                <StatCard icon="⚠️" label="Errores" value={totalErrors.toString()} variant={totalErrors > 0 ? 'error' : 'default'} />
                <StatCard icon="❌" label="Drops" value={totalDrops.toString()} variant={totalDrops > 0 ? 'warning' : 'default'} />
            {/if}
        </div>
        
        {#if !monitoringActive && !loading}
            <div class="monitor-placeholder">
                <span class="placeholder-icon">📊</span>
                <p>Inicia el monitoreo para ver métricas en tiempo real</p>
            </div>
        {/if}
    </section>
</div>

<style>
    .monitor-page { display: flex; flex-direction: column; gap: 1.5rem; }
    .card { background: var(--bg-card, #1a1a1a); border-radius: 12px; padding: 1.25rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0; color: var(--text-primary, #fff); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .monitor-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .monitor-placeholder { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem; background: var(--bg-elevated, #2b2b2b); border-radius: 12px; color: var(--text-muted, #666); }
    .placeholder-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.3; }
    .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
    .btn-primary { background: var(--primary, #00d4aa); color: #000; }
    .btn-primary:hover { background: #00e6b8; }
    .btn-danger { background: var(--error, #ff6b6b); color: #fff; }
    .btn-danger:hover { background: #ff5252; }
</style>
