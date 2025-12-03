<script lang="ts">
    /**
     * Phase 1: Adapter Check
     * Verifica el estado del adaptador de red local
     * DEPENDE DE: Usuario (100% controlable)
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
        weight: number; // Peso en score final (alto = depende de usuario)
    }
    
    const dispatch = createEventDispatcher<{
        complete: { result: PhaseResult };
    }>();
    
    export async function run(): Promise<PhaseResult> {
        result = { 
            status: 'running', 
            details: ['Detectando adaptadores de red...'],
            weight: 1.0 // 100% peso - totalmente controlable por usuario
        };
        
        try {
            const adapters: any[] = await invoke('get_network_adapters');
            const activeAdapter = adapters.find(a => a.is_connected);
            
            if (activeAdapter) {
                result = {
                    status: 'success',
                    details: [
                        `Adaptador: ${activeAdapter.name}`,
                        `Tipo: ${activeAdapter.adapter_type}`,
                        activeAdapter.speed ? `Velocidad link: ${activeAdapter.speed}` : 'Velocidad: Auto',
                        `Estado: Conectado`,
                        `MAC: ${activeAdapter.mac_address || 'N/A'}`
                    ].filter(Boolean),
                    weight: 1.0
                };
            } else if (adapters.length > 0) {
                result = {
                    status: 'warning',
                    details: [
                        'Adaptador encontrado pero desconectado',
                        `Disponibles: ${adapters.length}`,
                        ...adapters.slice(0, 3).map(a => `• ${a.name}`)
                    ],
                    recommendation: 'Verifica conexión física del cable o estado WiFi',
                    weight: 1.0
                };
            } else {
                result = {
                    status: 'error',
                    details: [
                        'No se encontraron adaptadores',
                        'Posible problema de drivers'
                    ],
                    recommendation: 'Abre Administrador de dispositivos y verifica drivers de red',
                    weight: 1.0
                };
            }
        } catch (e) {
            result = {
                status: 'error',
                details: [`Error: ${e}`],
                recommendation: 'Ejecutar como administrador',
                weight: 1.0
            };
        }
        
        dispatch('complete', { result });
        return result;
    }
</script>

<div class="phase-module" class:active={isActive} class:success={result?.status === 'success'} 
     class:warning={result?.status === 'warning'} class:error={result?.status === 'error'}>
    
    <div class="phase-header">
        <div class="phase-num">1</div>
        <div class="phase-title">
            <Icon name="wifi" size={18} />
            <span>Adaptador</span>
        </div>
        <div class="phase-badge user">Tu equipo</div>
    </div>
    
    {#if result?.status === 'running'}
        <div class="phase-loading">
            <div class="loading-bar"></div>
            <span>Detectando...</span>
        </div>
    {:else if result && result.status !== 'pending'}
        <div class="phase-results">
            <ul class="details-list">
                {#each result.details as detail}
                    <li>{detail}</li>
                {/each}
            </ul>
            {#if result.recommendation}
                <div class="recommendation">
                    <Icon name="info" size={12} />
                    {result.recommendation}
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
        border-color: var(--primary, #00d4aa);
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.15);
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
    
    .phase-badge.user {
        background: rgba(0, 212, 170, 0.2);
        color: #00d4aa;
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
        color: var(--primary, #00d4aa);
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
</style>
