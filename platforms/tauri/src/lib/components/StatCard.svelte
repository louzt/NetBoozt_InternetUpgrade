<script lang="ts">
    /**
     * NetBoozt - Stat Card Component
     * Tarjeta de estadística con icono
     * 
     * By LOUST (www.loust.pro)
     */
    
    export let icon: string = '📊';
    export let label: string = '';
    export let value: string | number = '';
    export let unit: string = '';
    export let trend: 'up' | 'down' | 'neutral' | null = null;
    export let trendValue: string = '';
    export let variant: 'default' | 'primary' | 'success' | 'warning' | 'error' = 'default';
</script>

<div class="stat-card {variant}">
    <div class="stat-icon">{icon}</div>
    <div class="stat-content">
        <span class="stat-label">{label}</span>
        <div class="stat-value-row">
            <span class="stat-value">{value}</span>
            {#if unit}
                <span class="stat-unit">{unit}</span>
            {/if}
        </div>
        {#if trend}
            <div class="stat-trend {trend}">
                <span class="trend-icon">
                    {#if trend === 'up'}↑{:else if trend === 'down'}↓{:else}→{/if}
                </span>
                <span class="trend-value">{trendValue}</span>
            </div>
        {/if}
    </div>
</div>

<style>
    .stat-card {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        background: var(--bg-elevated, #333);
        border-radius: 10px;
        padding: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .stat-card.primary {
        border-left: 3px solid var(--primary, #00d4aa);
    }
    
    .stat-card.success {
        border-left: 3px solid var(--success, #00ff88);
    }
    
    .stat-card.warning {
        border-left: 3px solid var(--warning, #fdcb6e);
    }
    
    .stat-card.error {
        border-left: 3px solid var(--error, #ff6b6b);
    }
    
    .stat-icon {
        font-size: 1.5rem;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-card, #2b2b2b);
        border-radius: 8px;
    }
    
    .stat-content {
        flex: 1;
        min-width: 0;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: var(--text-muted, #888);
        display: block;
        margin-bottom: 0.25rem;
    }
    
    .stat-value-row {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
    }
    
    .stat-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
    }
    
    .stat-unit {
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .stat-trend {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.7rem;
        margin-top: 0.25rem;
    }
    
    .stat-trend.up {
        color: var(--success, #00ff88);
    }
    
    .stat-trend.down {
        color: var(--error, #ff6b6b);
    }
    
    .stat-trend.neutral {
        color: var(--text-muted, #888);
    }
    
    .trend-icon {
        font-weight: bold;
    }
</style>
