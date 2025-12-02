<!--
    SpeedTestCard.svelte - Componente de prueba de velocidad
    Integrado con diagnosticStore para historial
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount, onDestroy } from 'svelte';
    import { invoke } from '$lib/tauri-bridge';
    import { listen, type UnlistenFn } from '@tauri-apps/api/event';
    import Icon from './Icon.svelte';
    import { diagnosticHistory, createSpeedTestReport } from '$lib/stores/diagnosticStore';
    
    // Props
    export let compact = false;
    export let saveToHistory = true; // Guardar en historial automáticamente
    
    const dispatch = createEventDispatcher();
    
    // Estado
    let testing = false;
    let stage: 'idle' | 'ping' | 'download' | 'upload' | 'complete' = 'idle';
    let progress = 0;
    let currentSpeed = 0;
    let message = '';
    let testStartTime = 0;
    
    // Último resultado
    let lastResult: {
        download_mbps: number;
        upload_mbps: number;
        ping_ms: number;
        jitter_ms: number;
        timestamp: string;
        server_name?: string;
    } | null = null;
    
    // Event listener
    let unlisten: UnlistenFn | null = null;
    
    onMount(async () => {
        // Escuchar eventos de progreso
        unlisten = await listen<any>('speedtest_progress', (event) => {
            const data = event.payload;
            stage = data.stage as any;
            progress = data.progress;
            currentSpeed = data.current_speed;
            message = data.message;
        });
    });
    
    onDestroy(() => {
        if (unlisten) unlisten();
    });
    
    async function runSpeedTest() {
        if (testing) return;
        
        testing = true;
        stage = 'ping';
        progress = 0;
        message = 'Iniciando...';
        lastResult = null;
        testStartTime = Date.now();
        
        try {
            const result = await invoke<any>('run_speed_test');
            lastResult = result;
            stage = 'complete';
            
            // Guardar en historial si está habilitado
            if (saveToHistory) {
                const report = createSpeedTestReport({
                    downloadMbps: result.download_mbps,
                    uploadMbps: result.upload_mbps,
                    pingMs: result.ping_ms,
                    jitterMs: result.jitter_ms,
                    serverName: result.server_name || 'Cloudflare'
                });
                
                // Agregar duración
                const duration = Date.now() - testStartTime;
                diagnosticHistory.add({
                    ...report,
                    duration
                });
            }
            
            dispatch('complete', result);
        } catch (e) {
            console.error('Speed test error:', e);
            message = `Error: ${e}`;
            stage = 'idle';
        } finally {
            testing = false;
        }
    }
    
    function getStageIcon(s: string): string {
        const icons: Record<string, string> = {
            'idle': '🚀',
            'ping': '🏓',
            'download': '📥',
            'upload': '📤',
            'complete': '✅'
        };
        return icons[s] || '⏳';
    }
    
    function getStageLabel(s: string): string {
        const labels: Record<string, string> = {
            'idle': 'Listo',
            'ping': 'Midiendo latencia',
            'download': 'Probando descarga',
            'upload': 'Probando subida',
            'complete': 'Completado'
        };
        return labels[s] || 'Procesando';
    }
    
    function formatSpeed(mbps: number): string {
        if (mbps >= 1000) {
            return `${(mbps / 1000).toFixed(2)} Gbps`;
        }
        return `${mbps.toFixed(2)} Mbps`;
    }
    
    function formatDate(iso: string): string {
        const date = new Date(iso);
        return date.toLocaleTimeString('es-MX', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    // Rating de velocidad
    function getSpeedRating(download: number): { label: string; color: string; emoji: string } {
        if (download >= 100) return { label: 'Excelente', color: '#00d4aa', emoji: '🚀' };
        if (download >= 50) return { label: 'Muy Buena', color: '#4CAF50', emoji: '✨' };
        if (download >= 25) return { label: 'Buena', color: '#8BC34A', emoji: '👍' };
        if (download >= 10) return { label: 'Aceptable', color: '#FFC107', emoji: '👌' };
        if (download >= 5) return { label: 'Regular', color: '#FF9800', emoji: '😐' };
        return { label: 'Lenta', color: '#F44336', emoji: '🐌' };
    }
    
    // Rating reactivo
    $: currentRating = lastResult ? getSpeedRating(lastResult.download_mbps) : null;
</script>

<div class="speedtest-card" class:compact>
    {#if !compact}
        <div class="card-header">
            <h3>🚀 Speed Test</h3>
            <span class="subtitle">Prueba tu velocidad máxima</span>
        </div>
    {/if}
    
    <!-- Resultados o botón de inicio -->
    {#if lastResult && stage === 'complete' && currentRating}
        <!-- Resultados -->
        <div class="results">
            <div class="rating-badge" style="--rating-color: {currentRating.color}">
                <span class="rating-emoji">{currentRating.emoji}</span>
                <span class="rating-label">{currentRating.label}</span>
            </div>
            
            <div class="speeds">
                <div class="speed-item download">
                    <span class="speed-icon">📥</span>
                    <div class="speed-info">
                        <span class="speed-value">{formatSpeed(lastResult.download_mbps)}</span>
                        <span class="speed-label">Descarga</span>
                    </div>
                </div>
                
                <div class="speed-item upload">
                    <span class="speed-icon">📤</span>
                    <div class="speed-info">
                        <span class="speed-value">{formatSpeed(lastResult.upload_mbps)}</span>
                        <span class="speed-label">Subida</span>
                    </div>
                </div>
            </div>
            
            <div class="latency-info">
                <span class="ping">🏓 {lastResult.ping_ms.toFixed(0)}ms</span>
                <span class="jitter">📊 Jitter: {lastResult.jitter_ms.toFixed(1)}ms</span>
                <span class="time">🕐 {formatDate(lastResult.timestamp)}</span>
            </div>
            
            <button class="btn btn-secondary" on:click={runSpeedTest} disabled={testing}>
                <Icon name="refresh-cw" size={14} />
                Probar de nuevo
            </button>
        </div>
    {:else if testing}
        <!-- En progreso -->
        <div class="testing">
            <div class="stage-indicator">
                <span class="stage-icon">{getStageIcon(stage)}</span>
                <span class="stage-label">{getStageLabel(stage)}</span>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            
            {#if stage === 'download' || stage === 'upload'}
                <div class="current-speed">
                    <span class="speed-live">{currentSpeed.toFixed(2)}</span>
                    <span class="speed-unit">Mbps</span>
                </div>
            {/if}
            
            <p class="message">{message}</p>
        </div>
    {:else}
        <!-- Idle - Botón de inicio -->
        <div class="idle">
            <button class="btn btn-primary btn-lg start-btn" on:click={runSpeedTest}>
                <span class="start-icon">🚀</span>
                <span>Iniciar Speed Test</span>
            </button>
            <p class="hint">Mide tu velocidad máxima de internet</p>
        </div>
    {/if}
</div>

<style>
    .speedtest-card {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .speedtest-card.compact {
        padding: 1rem;
    }
    
    .card-header {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .card-header h3 {
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        color: var(--text-primary, #fff);
    }
    
    .subtitle {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    /* Idle state */
    .idle {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 0;
    }
    
    .start-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 2rem;
        font-size: 1rem;
        border-radius: 50px;
        background: linear-gradient(135deg, var(--primary, #00d4aa), #00b894);
        border: none;
        color: #000;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3);
    }
    
    .start-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4);
    }
    
    .start-icon {
        font-size: 1.25rem;
    }
    
    .hint {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
        margin: 0;
    }
    
    /* Testing state */
    .testing {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 1rem 0;
    }
    
    .stage-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .stage-icon {
        font-size: 1.5rem;
        animation: pulse 1s infinite;
    }
    
    .stage-label {
        font-size: 0.875rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary, #00d4aa), #00e6b8);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .current-speed {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
    }
    
    .speed-live {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary, #00d4aa);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .speed-unit {
        font-size: 1rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .message {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
        margin: 0;
    }
    
    /* Results state */
    .results {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .rating-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(0, 212, 170, 0.1);
        border: 2px solid var(--rating-color);
        border-radius: 50px;
    }
    
    .rating-emoji {
        font-size: 1.25rem;
    }
    
    .rating-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--rating-color);
    }
    
    .speeds {
        display: flex;
        gap: 2rem;
        justify-content: center;
    }
    
    .speed-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .speed-icon {
        font-size: 1.5rem;
    }
    
    .speed-info {
        display: flex;
        flex-direction: column;
    }
    
    .speed-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .speed-label {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .speed-item.download .speed-value {
        color: var(--primary, #00d4aa);
    }
    
    .speed-item.upload .speed-value {
        color: #9C27B0;
    }
    
    .latency-info {
        display: flex;
        gap: 1rem;
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    /* Buttons */
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.8125rem;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: all 0.15s;
    }
    
    .btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    .btn-primary {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    .btn-secondary {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-secondary, #a0a0a0);
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .btn-secondary:hover:not(:disabled) {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
</style>
