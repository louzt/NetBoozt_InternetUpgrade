<script lang="ts">
    /**
     * Phase 3: ISP Connectivity Check
     * Verifica conectividad con el proveedor de internet
     * DEPENDE DE: ISP (80%) - Poco control del usuario
     */
    import { createEventDispatcher } from 'svelte';
    import { invoke } from '$lib/tauri-bridge';
    import Icon from '../Icon.svelte';
    
    export let isActive = false;
    export let result: PhaseResult | null = null;
    
    interface PhaseResult {
        status: 'pending' | 'running' | 'success' | 'warning' | 'error';
        details: string[];
        latency?: number;
        recommendation?: string;
        weight: number;
    }
    
    const dispatch = createEventDispatcher<{
        complete: { result: PhaseResult };
    }>();
    
    export async function run(): Promise<PhaseResult> {
        result = { 
            status: 'running', 
            details: ['Verificando conectividad ISP...'],
            weight: 0.3 // Bajo peso - no depende del usuario
        };
        
        try {
            const diagnostic: any = await invoke('run_network_diagnostic');
            
            if (diagnostic.isp_ok) {
                const latency = diagnostic.isp_latency_ms;
                
                result = {
                    status: 'success',
                    latency,
                    details: [
                        'Conectividad ISP OK',
                        `Latencia al ISP: ${latency.toFixed(0)} ms`,
                        'Salida a internet funcionando',
                        'Sin bloqueos detectados'
                    ],
                    weight: 0.3
                };
            } else {
                result = {
                    status: 'error',
                    details: [
                        'Problema de conectividad con ISP',
                        'No se alcanza puntos externos',
                        'Posible corte del servicio'
                    ],
                    recommendation: 'Este problema depende de tu ISP. Contacta soporte técnico o espera.',
                    weight: 0.3
                };
            }
        } catch (e) {
            result = {
                status: 'error',
                details: [`Error: ${e}`],
                recommendation: 'Verificar estado del servicio',
                weight: 0.3
            };
        }
        
        dispatch('complete', { result });
        return result;
    }
</script>

<div class="phase-module" class:active={isActive} class:success={result?.status === 'success'} 
     class:warning={result?.status === 'warning'} class:error={result?.status === 'error'}>
    
    <div class="phase-header">
        <div class="phase-num external">3</div>
        <div class="phase-title">
            <Icon name="globe" size={18} />
            <span>ISP</span>
        </div>
        <div class="phase-badge external">Proveedor</div>
    </div>
    
    {#if result?.status === 'running'}
        <div class="phase-loading">
            <div class="loading-bar external"></div>
            <span>Verificando ISP...</span>
        </div>
    {:else if result && result.status !== 'pending'}
        <div class="phase-results">
            {#if result.latency !== undefined}
                <div class="latency-display">
                    <span class="latency-value">{result.latency.toFixed(0)}</span>
                    <span class="latency-unit">ms</span>
                </div>
            {/if}
            <ul class="details-list">
                {#each result.details as detail}
                    <li>{detail}</li>
                {/each}
            </ul>
            {#if result.recommendation}
                <div class="recommendation external">
                    <Icon name="alert-triangle" size={12} />
                    {result.recommendation}
                </div>
            {/if}
            {#if result.status === 'error'}
                <div class="external-notice">
                    <Icon name="info" size={12} />
                    Este factor NO depende de ti - no afecta el score de optimización
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .phase-module {
        background: rgba(30, 30, 30, 0.6);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .phase-module.active {
        border-color: #ff9800;
        box-shadow: 0 0 20px rgba(255, 152, 0, 0.15);
    }
    
    .phase-module.success { border-color: #00ff88; }
    .phase-module.warning { border-color: #ffc107; }
    .phase-module.error { border-color: #ff4444; }
    
    .phase-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .phase-num {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--primary, #00d4aa);
        border-radius: 50%;
        font-size: 0.75rem;
        font-weight: 700;
        color: #000;
    }
    
    .phase-num.external {
        background: #ff9800;
    }
    
    .phase-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .phase-badge {
        margin-left: auto;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 500;
    }
    
    .phase-badge.external {
        background: rgba(255, 152, 0, 0.2);
        color: #ff9800;
    }
    
    .phase-loading {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }
    
    .loading-bar {
        flex: 1;
        height: 4px;
        background: var(--border, #3d3d3d);
        border-radius: 2px;
        overflow: hidden;
        position: relative;
    }
    
    .loading-bar::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 30%;
        background: var(--primary, #00d4aa);
        animation: loading-slide 1s ease-in-out infinite;
    }
    
    .loading-bar.external::after {
        background: #ff9800;
    }
    
    @keyframes loading-slide {
        0% { left: -30%; }
        100% { left: 100%; }
    }
    
    .phase-loading span {
        font-size: 0.75rem;
        color: var(--text-muted, #888);
    }
    
    .phase-results {
        padding-top: 0.5rem;
    }
    
    .latency-display {
        display: inline-flex;
        align-items: baseline;
        gap: 0.25rem;
        padding: 0.35rem 0.75rem;
        background: rgba(0, 212, 170, 0.1);
        border-radius: 6px;
        margin-bottom: 0.75rem;
    }
    
    .latency-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--primary, #00d4aa);
    }
    
    .latency-unit {
        font-size: 0.75rem;
        color: var(--text-muted, #888);
    }
    
    .details-list {
        list-style: none;
        margin: 0;
        padding: 0;
    }
    
    .details-list li {
        font-size: 0.8rem;
        color: var(--text-secondary, #a0a0a0);
        padding: 0.2rem 0;
        padding-left: 1rem;
        position: relative;
    }
    
    .details-list li::before {
        content: '•';
        position: absolute;
        left: 0;
        color: #ff9800;
    }
    
    .recommendation {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        margin-top: 0.75rem;
        padding: 0.5rem 0.75rem;
        background: rgba(255, 193, 7, 0.1);
        border-radius: 6px;
        font-size: 0.75rem;
        color: #ffc107;
    }
    
    .recommendation.external {
        background: rgba(255, 152, 0, 0.1);
        color: #ff9800;
    }
    
    .external-notice {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(100, 100, 100, 0.1);
        border-radius: 6px;
        font-size: 0.7rem;
        color: var(--text-muted, #888);
        font-style: italic;
    }
</style>
