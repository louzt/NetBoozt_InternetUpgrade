<script lang="ts">
    /**
     * Phase 5: Speed Test
     * Mide velocidad de conexión
     * DEPENDE DE: ISP (90%) - Informativo, bajo peso en score
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
        speed?: {
            download: number;
            upload: number;
            ping: number;
        };
    }
    
    const dispatch = createEventDispatcher<{
        complete: { result: PhaseResult };
    }>();
    
    let progress = 0;
    let progressPhase = '';
    
    export async function run(): Promise<PhaseResult> {
        result = { 
            status: 'running', 
            details: ['Preparando speed test...'],
            weight: 0.2 // Muy bajo peso - depende del ISP
        };
        progress = 0;
        progressPhase = 'Conectando...';
        
        try {
            // Simular progreso mientras corre el test
            const progressInterval = setInterval(() => {
                if (progress < 90) {
                    progress += 5;
                    if (progress < 30) progressPhase = 'Midiendo ping...';
                    else if (progress < 60) progressPhase = 'Test de descarga...';
                    else progressPhase = 'Test de subida...';
                }
            }, 200);
            
            const speedResult: any = await invoke('run_speed_test');
            clearInterval(progressInterval);
            progress = 100;
            
            if (speedResult && speedResult.download_mbps > 0) {
                const download = speedResult.download_mbps;
                const upload = speedResult.upload_mbps || 0;
                const ping = speedResult.ping_ms || 0;
                
                let status: 'success' | 'warning' = 'success';
                let recommendation: string | undefined;
                
                if (download < 10) {
                    status = 'warning';
                    recommendation = 'Velocidad baja. Las optimizaciones TCP de NetBoozt pueden ayudar.';
                } else if (download < 50 && ping > 50) {
                    recommendation = 'Considera aplicar perfil de optimizaciones';
                }
                
                result = {
                    status,
                    details: [
                        `Download: ${download.toFixed(1)} Mbps`,
                        `Upload: ${upload.toFixed(1)} Mbps`,
                        `Ping: ${ping.toFixed(0)} ms`,
                        download > 100 ? 'Velocidad excelente' : download > 50 ? 'Velocidad buena' : 'Velocidad mejorable'
                    ],
                    recommendation,
                    weight: 0.2,
                    speed: { download, upload, ping }
                };
            } else {
                result = {
                    status: 'warning',
                    details: [
                        'No se pudo completar speed test',
                        'Conexión funcional sin medición',
                        'Usa fast.com o speedtest.net'
                    ],
                    recommendation: 'El test de velocidad es informativo. Tu internet funciona.',
                    weight: 0.2
                };
            }
        } catch (e) {
            progress = 0;
            result = {
                status: 'warning',
                details: [
                    'Speed test no disponible',
                    `${e}`,
                    'Conexión funciona correctamente'
                ],
                weight: 0.2
            };
        }
        
        dispatch('complete', { result });
        return result;
    }
</script>

<div class="phase-module" class:active={isActive} class:success={result?.status === 'success'} 
     class:warning={result?.status === 'warning'} class:error={result?.status === 'error'}>
    
    <div class="phase-header">
        <div class="phase-num external">5</div>
        <div class="phase-title">
            <Icon name="zap" size={18} />
            <span>Velocidad</span>
        </div>
        <div class="phase-badge external">Informativo</div>
    </div>
    
    {#if result?.status === 'running'}
        <div class="speed-progress">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <span class="progress-text">{progressPhase}</span>
        </div>
    {:else if result && result.status !== 'pending'}
        <div class="phase-results">
            {#if result.speed}
                <div class="speed-results">
                    <div class="speed-metric download">
                        <Icon name="download" size={16} />
                        <span class="speed-value">{result.speed.download.toFixed(1)}</span>
                        <span class="speed-unit">Mbps</span>
                    </div>
                    <div class="speed-metric upload">
                        <Icon name="upload" size={16} />
                        <span class="speed-value">{result.speed.upload.toFixed(1)}</span>
                        <span class="speed-unit">Mbps</span>
                    </div>
                    <div class="speed-metric ping">
                        <Icon name="activity" size={16} />
                        <span class="speed-value">{result.speed.ping.toFixed(0)}</span>
                        <span class="speed-unit">ms</span>
                    </div>
                </div>
            {/if}
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
            <div class="external-notice">
                <Icon name="info" size={12} />
                La velocidad depende de tu ISP - es solo informativo
            </div>
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
        border-color: #3b82f6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
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
        background: #3b82f6;
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
        background: rgba(59, 130, 246, 0.2);
        color: #3b82f6;
    }
    
    .speed-progress {
        padding: 0.75rem 0;
    }
    
    .progress-bar {
        height: 8px;
        background: var(--border, #3d3d3d);
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #00d4aa);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .progress-text {
        font-size: 0.75rem;
        color: var(--text-muted, #888);
    }
    
    .phase-results {
        padding-top: 0.5rem;
    }
    
    .speed-results {
        display: flex;
        gap: 1rem;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;
    }
    
    .speed-metric {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.5rem 0.75rem;
        background: rgba(30, 30, 30, 0.8);
        border-radius: 8px;
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .speed-metric.download { color: #00ff88; }
    .speed-metric.upload { color: #3b82f6; }
    .speed-metric.ping { color: #ffc107; }
    
    .speed-value {
        font-size: 1.1rem;
        font-weight: 700;
    }
    
    .speed-unit {
        font-size: 0.7rem;
        opacity: 0.7;
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
        color: #3b82f6;
    }
    
    .recommendation {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        margin-top: 0.75rem;
        padding: 0.5rem 0.75rem;
        background: rgba(59, 130, 246, 0.1);
        border-radius: 6px;
        font-size: 0.75rem;
        color: #3b82f6;
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
