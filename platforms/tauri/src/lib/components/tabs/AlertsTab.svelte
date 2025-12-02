<!--
    AlertsTab.svelte - Tab de Alertas
    By LOUST
-->
<script lang="ts">
    import SkeletonCard from '../SkeletonCard.svelte';
    
    export let loading = false;
    export let alerts: any[] = [];
    export let alertThresholds = { latency_high: 100, packet_loss: 2, speed_low: 10, dns_failure: 3 };
</script>

<div class="alerts-page">
    <section class="card">
        <h2>🔔 Umbrales de Alerta</h2>
        <div class="threshold-grid">
            <div class="threshold-item">
                <label for="threshold-latency">Latencia Alta (ms)</label>
                <input id="threshold-latency" type="number" bind:value={alertThresholds.latency_high} min="10" max="1000" />
            </div>
            <div class="threshold-item">
                <label for="threshold-packet-loss">Pérdida de Paquetes (%)</label>
                <input id="threshold-packet-loss" type="number" bind:value={alertThresholds.packet_loss} min="0.1" max="50" step="0.1" />
            </div>
            <div class="threshold-item">
                <label for="threshold-speed-low">Velocidad Baja (Mbps)</label>
                <input id="threshold-speed-low" type="number" bind:value={alertThresholds.speed_low} min="1" max="1000" />
            </div>
            <div class="threshold-item">
                <label for="threshold-dns-failure">Fallas DNS</label>
                <input id="threshold-dns-failure" type="number" bind:value={alertThresholds.dns_failure} min="1" max="10" />
            </div>
        </div>
    </section>
    
    <section class="card">
        <h2>📜 Historial de Alertas</h2>
        {#if loading}
            {#each [1,2,3] as _}
                <SkeletonCard variant="alert" />
            {/each}
        {:else if alerts.length === 0}
            <div class="empty-state">
                <span class="empty-icon">✅</span>
                <p>No hay alertas recientes. ¡Tu red está funcionando bien!</p>
            </div>
        {:else}
            <div class="alerts-list">
                {#each alerts as alert}
                    <div class="alert-item {alert.severity}" class:resolved={alert.resolved}>
                        <span class="alert-icon">{alert.severity === 'critical' ? '🔴' : alert.severity === 'warning' ? '🟡' : 'ℹ️'}</span>
                        <div class="alert-content">
                            <span class="alert-message">{alert.message}</span>
                            <span class="alert-time">{new Date(alert.timestamp).toLocaleString()}</span>
                        </div>
                        {#if alert.resolved}<span class="resolved-badge">Resuelto</span>{/if}
                    </div>
                {/each}
            </div>
        {/if}
    </section>
</div>

<style>
    .alerts-page { display: flex; flex-direction: column; gap: 1.5rem; }
    .card { background: var(--bg-card, #1a1a1a); border-radius: 12px; padding: 1.25rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-primary, #fff); }
    .threshold-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
    .threshold-item { display: flex; flex-direction: column; gap: 0.375rem; }
    .threshold-item label { font-size: 0.75rem; color: var(--text-muted, #666); }
    .threshold-item input { background: var(--bg-elevated, #2b2b2b); border: 1px solid var(--border, #3d3d3d); border-radius: 6px; padding: 0.5rem; color: var(--text-primary, #fff); font-size: 0.875rem; }
    .alerts-list { display: flex; flex-direction: column; gap: 0.5rem; }
    .alert-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: var(--bg-elevated, #2b2b2b); border-radius: 8px; border-left: 3px solid var(--border, #3d3d3d); }
    .alert-item.critical { border-left-color: var(--error, #ff6b6b); }
    .alert-item.warning { border-left-color: var(--warning, #fdcb6e); }
    .alert-item.resolved { opacity: 0.5; }
    .alert-icon { font-size: 1.25rem; }
    .alert-content { flex: 1; }
    .alert-message { display: block; font-size: 0.8125rem; color: var(--text-primary, #fff); }
    .alert-time { font-size: 0.7rem; color: var(--text-muted, #666); }
    .resolved-badge { font-size: 0.65rem; color: var(--success, #00ff88); background: rgba(0, 255, 136, 0.1); padding: 0.2rem 0.5rem; border-radius: 4px; }
    .empty-state { display: flex; flex-direction: column; align-items: center; padding: 2rem; color: var(--text-muted, #666); text-align: center; }
    .empty-icon { font-size: 2.5rem; margin-bottom: 0.75rem; opacity: 0.5; }
</style>
