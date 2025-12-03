<script lang="ts">
    /**
     * NetBoozt - Stat Card Component
     * Tarjeta de estadística con icono (Glassmorphism)
     * 
     * By LOUST (www.loust.pro)
     */
    import Icon from './Icon.svelte';
    
    export let icon: string = 'activity'; // Ahora espera nombre de icono de Icon.svelte
    export let label: string = '';
    export let value: string | number = '';
    export let unit: string = '';
    export let trend: 'up' | 'down' | 'neutral' | null = null;
    export let trendValue: string = '';
    export let variant: 'default' | 'primary' | 'success' | 'warning' | 'error' = 'default';
    
    // Mapeo de iconos legacy a Icon component
    const iconMap: Record<string, string> = {
        '📥': 'arrow-down',
        '📤': 'arrow-up', 
        '🏓': 'activity',
        '⏱️': 'clock',
        '📊': 'bar-chart',
        '🚀': 'zap',
    };
    
    $: iconName = iconMap[icon] || icon;
    
    // Color del icono según variante
    function getIconColor(v: string): string {
        switch (v) {
            case 'primary': return 'var(--primary, #00d4aa)';
            case 'success': return 'var(--success, #00ff88)';
            case 'warning': return 'var(--warning, #fdcb6e)';
            case 'error': return 'var(--error, #ff6b6b)';
            default: return 'var(--text-secondary, #a0a0a0)';
        }
    }
</script>

<div class="stat-card {variant}">
    <div class="stat-icon" style="color: {getIconColor(variant)}">
        <Icon name={iconName} size={22} />
    </div>
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
                    {#if trend === 'up'}<Icon name="trending-up" size={12} />{:else if trend === 'down'}<Icon name="arrow-down" size={12} />{:else}<Icon name="arrow-right" size={12} />{/if}
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
        background: rgba(45, 45, 45, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        transition: transform 0.2s, box-shadow 0.2s, background 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        background: rgba(50, 50, 50, 0.7);
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
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        background: rgba(0, 0, 0, 0.25);
        border-radius: 10px;
        flex-shrink: 0;
    }
    
    .stat-content {
        flex: 1;
        min-width: 0;
    }
    
    .stat-label {
        font-size: 0.6875rem;
        color: var(--text-muted, #888);
        display: block;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        font-weight: 500;
    }
    
    .stat-value-row {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
    }
    
    .stat-value {
        font-size: 1.375rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    
    .stat-unit {
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
        font-weight: 500;
    }
    
    .stat-trend {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.7rem;
        margin-top: 0.35rem;
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
        display: flex;
        align-items: center;
    }
</style>
