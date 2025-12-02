<script lang="ts">
    /**
     * NetBoozt - Diagnostic Chain Component
     * Visualización de la cadena de diagnóstico de red
     * 
     * By LOUST (www.loust.pro)
     */
    
    import type { DiagnosticResult, NetworkHealth } from '$lib/types';
    
    export let diagnostic: DiagnosticResult | null = null;
    export let loading: boolean = false;
    
    const healthColors: Record<NetworkHealth, string> = {
        Excellent: '#00d4aa',
        Good: '#4CAF50',
        Fair: '#FFC107',
        Poor: '#FF9800',
        Bad: '#F44336',
        Down: '#9E9E9E'
    };
    
    const healthEmojis: Record<NetworkHealth, string> = {
        Excellent: '🟢',
        Good: '🟢',
        Fair: '🟡',
        Poor: '🟠',
        Bad: '🔴',
        Down: '⚫'
    };
</script>

<div class="diagnostic-container">
    {#if loading}
        <div class="loading-state">
            <div class="spinner"></div>
            <p>Ejecutando diagnóstico...</p>
        </div>
    {:else if diagnostic}
        <!-- Health Badge -->
        <div class="health-section">
            <div 
                class="health-badge"
                style="--health-color: {healthColors[diagnostic.health]}"
            >
                <span class="health-emoji">{healthEmojis[diagnostic.health]}</span>
                <span class="health-text">{diagnostic.health}</span>
            </div>
            {#if diagnostic.score > 0}
                <div class="score-badge">
                    <span class="score-value">{diagnostic.score.toFixed(0)}</span>
                    <span class="score-label">/100</span>
                </div>
            {/if}
        </div>
        
        <!-- Diagnostic Chain -->
        <div class="chain">
            <!-- Adapter -->
            <div class="chain-step" class:ok={diagnostic.adapter_ok} class:error={!diagnostic.adapter_ok}>
                <div class="step-icon">
                    {diagnostic.adapter_ok ? '✅' : '❌'}
                </div>
                <div class="step-info">
                    <span class="step-label">Adaptador</span>
                    <span class="step-detail">{diagnostic.adapter_name || 'N/A'}</span>
                </div>
            </div>
            
            <div class="chain-arrow">→</div>
            
            <!-- Router -->
            <div class="chain-step" class:ok={diagnostic.router_ok} class:error={!diagnostic.router_ok && diagnostic.adapter_ok}>
                <div class="step-icon">
                    {diagnostic.router_ok ? '✅' : (diagnostic.adapter_ok ? '❌' : '⏸️')}
                </div>
                <div class="step-info">
                    <span class="step-label">Router</span>
                    <span class="step-latency">
                        {diagnostic.router_latency_ms > 0 ? `${diagnostic.router_latency_ms.toFixed(0)}ms` : '---'}
                    </span>
                </div>
            </div>
            
            <div class="chain-arrow">→</div>
            
            <!-- ISP -->
            <div class="chain-step" class:ok={diagnostic.isp_ok} class:error={!diagnostic.isp_ok && diagnostic.router_ok}>
                <div class="step-icon">
                    {diagnostic.isp_ok ? '✅' : (diagnostic.router_ok ? '❌' : '⏸️')}
                </div>
                <div class="step-info">
                    <span class="step-label">ISP</span>
                    <span class="step-latency">
                        {diagnostic.isp_latency_ms > 0 ? `${diagnostic.isp_latency_ms.toFixed(0)}ms` : '---'}
                    </span>
                </div>
            </div>
            
            <div class="chain-arrow">→</div>
            
            <!-- DNS -->
            <div class="chain-step" class:ok={diagnostic.dns_ok} class:error={!diagnostic.dns_ok && diagnostic.isp_ok}>
                <div class="step-icon">
                    {diagnostic.dns_ok ? '✅' : (diagnostic.isp_ok ? '❌' : '⏸️')}
                </div>
                <div class="step-info">
                    <span class="step-label">DNS</span>
                    <span class="step-latency">
                        {diagnostic.dns_latency_ms > 0 ? `${diagnostic.dns_latency_ms.toFixed(0)}ms` : '---'}
                    </span>
                </div>
            </div>
        </div>
        
        <!-- Recommendation -->
        {#if diagnostic.recommendation}
            <div class="recommendation">
                <span class="recommendation-icon">💡</span>
                <span class="recommendation-text">{diagnostic.recommendation}</span>
            </div>
        {/if}
    {:else}
        <div class="empty-state">
            <span class="empty-icon">🔍</span>
            <p>Ejecuta un diagnóstico para analizar tu conexión</p>
        </div>
    {/if}
</div>

<style>
    .diagnostic-container {
        padding: 1rem;
    }
    
    .loading-state,
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        gap: 1rem;
        color: var(--text-muted, #888);
    }
    
    .empty-icon {
        font-size: 2.5rem;
        opacity: 0.5;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    /* Health Section */
    .health-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .health-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.25rem;
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid var(--health-color);
        border-radius: 50px;
    }
    
    .score-badge {
        display: flex;
        align-items: baseline;
        gap: 0.15rem;
        padding: 0.25rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 20px;
    }
    
    .score-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--health-color, var(--primary, #00d4aa));
    }
    
    .score-label {
        font-size: 0.75rem;
        color: var(--text-muted, #888);
    }
    
    .health-emoji {
        font-size: 1.25rem;
    }
    
    .health-text {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--health-color);
    }
    
    /* Chain */
    .chain {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin: 1.5rem 0;
    }
    
    .chain-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0.75rem 1rem;
        background: var(--bg-elevated, #333);
        border-radius: 10px;
        border: 2px solid var(--border, #3d3d3d);
        min-width: 90px;
        transition: all 0.2s;
    }
    
    .chain-step.ok {
        border-color: var(--success, #00ff88);
    }
    
    .chain-step.error {
        border-color: var(--error, #ff6b6b);
        animation: pulse-error 2s infinite;
    }
    
    @keyframes pulse-error {
        0%, 100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.4); }
        50% { box-shadow: 0 0 10px 3px rgba(255, 107, 107, 0.2); }
    }
    
    .step-icon {
        font-size: 1.5rem;
        margin-bottom: 0.25rem;
    }
    
    .step-info {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .step-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .step-detail {
        font-size: 0.65rem;
        color: var(--text-muted, #888);
        max-width: 80px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .step-latency {
        font-size: 0.65rem;
        color: var(--text-muted, #888);
        font-family: monospace;
    }
    
    .chain-arrow {
        color: var(--text-muted, #888);
        font-size: 1.25rem;
    }
    
    /* Recommendation */
    .recommendation {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 1rem;
        background: rgba(0, 212, 170, 0.1);
        border-left: 4px solid var(--primary, #00d4aa);
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
    }
    
    .recommendation-icon {
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    
    .recommendation-text {
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
        line-height: 1.5;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Responsive */
    @media (max-width: 600px) {
        .chain {
            flex-direction: column;
        }
        
        .chain-arrow {
            transform: rotate(90deg);
        }
    }
</style>
