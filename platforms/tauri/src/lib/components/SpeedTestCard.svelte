<!--
    SpeedTestCard.svelte - Componente de prueba de velocidad
    Diseño moderno con efecto Matrix pulse y animación central
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
    export let saveToHistory = true;
    export let autoResetSeconds = 30; // Tiempo para volver al estado idle
    
    const dispatch = createEventDispatcher();
    
    // Servidores disponibles
    const SERVERS = [
        { id: 'cloudflare', name: 'Cloudflare', desc: 'Recomendado - Servidores edge globales, baja latencia', default: true },
        { id: 'fast', name: 'Fast.com', desc: 'Netflix - Bueno para streaming' },
        { id: 'speedtest', name: 'Speedtest.net', desc: 'Ookla - Popular, muchos servidores' },
        { id: 'custom', name: 'Personalizado', desc: 'Especifica tu propio servidor' },
    ];
    
    // Estado
    let testing = false;
    let stage: 'idle' | 'ping' | 'download' | 'upload' | 'complete' = 'idle';
    let progress = 0;
    let currentSpeed = 0;
    let message = '';
    let testStartTime = 0;
    let showTransition = false;
    let selectedServer = 'cloudflare';
    let showServerSelect = false;
    let customServerUrl = '';
    let autoResetTimer: ReturnType<typeof setTimeout> | null = null;
    let resetCountdown = 0;
    let countdownInterval: ReturnType<typeof setInterval> | null = null;
    
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
        if (autoResetTimer) clearTimeout(autoResetTimer);
        if (countdownInterval) clearInterval(countdownInterval);
    });
    
    function startAutoReset() {
        if (autoResetTimer) clearTimeout(autoResetTimer);
        if (countdownInterval) clearInterval(countdownInterval);
        
        if (autoResetSeconds > 0) {
            resetCountdown = autoResetSeconds;
            
            // Actualizar countdown cada segundo
            countdownInterval = setInterval(() => {
                resetCountdown--;
                if (resetCountdown <= 0) {
                    if (countdownInterval) clearInterval(countdownInterval);
                }
            }, 1000);
            
            autoResetTimer = setTimeout(() => {
                stage = 'idle';
                lastResult = null;
                resetCountdown = 0;
                if (countdownInterval) clearInterval(countdownInterval);
            }, autoResetSeconds * 1000);
        }
    }
    
    function cancelAutoReset() {
        if (autoResetTimer) {
            clearTimeout(autoResetTimer);
            autoResetTimer = null;
        }
        if (countdownInterval) {
            clearInterval(countdownInterval);
            countdownInterval = null;
        }
        resetCountdown = 0;
    }
    
    async function runSpeedTest() {
        if (testing) return;
        if (autoResetTimer) clearTimeout(autoResetTimer);
        
        testing = true;
        showTransition = false;
        stage = 'ping';
        progress = 0;
        message = 'Iniciando...';
        lastResult = null;
        testStartTime = Date.now();
        
        try {
            const result = await invoke<any>('run_speed_test', { server: selectedServer });
            lastResult = result;
            
            showTransition = true;
            await new Promise(r => setTimeout(r, 800));
            showTransition = false;
            
            stage = 'complete';
            
            if (saveToHistory) {
                const report = createSpeedTestReport({
                    downloadMbps: result.download_mbps,
                    uploadMbps: result.upload_mbps,
                    pingMs: result.ping_ms,
                    jitterMs: result.jitter_ms,
                    serverName: result.server_name || SERVERS.find(s => s.id === selectedServer)?.name || 'Unknown'
                });
                const duration = Date.now() - testStartTime;
                diagnosticHistory.add({ ...report, duration });
            }
            
            dispatch('complete', result);
            startAutoReset();
        } catch (e) {
            console.error('Speed test error:', e);
            message = `Error: ${e}`;
            stage = 'idle';
        } finally {
            testing = false;
        }
    }
    
    function selectServer(id: string) {
        selectedServer = id;
        showServerSelect = false;
    }
    
    function getStageIcon(s: string): string {
        const icons: Record<string, string> = {
            'idle': 'play',
            'ping': 'activity',
            'download': 'arrow-down',
            'upload': 'arrow-up',
            'complete': 'check-circle'
        };
        return icons[s] || 'loader';
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
    
    // Rating de velocidad - con iconos SVG personalizados
    function getSpeedRating(download: number): { label: string; color: string; icon: string; gradient: string } {
        if (download >= 100) return { label: 'Excelente', color: '#00d4aa', icon: 'rocket', gradient: 'linear-gradient(135deg, #00d4aa, #00f5c4)' };
        if (download >= 50) return { label: 'Muy Buena', color: '#00e676', icon: 'zap', gradient: 'linear-gradient(135deg, #00e676, #69f0ae)' };
        if (download >= 25) return { label: 'Buena', color: '#7c4dff', icon: 'wifi', gradient: 'linear-gradient(135deg, #7c4dff, #b388ff)' };
        if (download >= 10) return { label: 'Aceptable', color: '#ffc107', icon: 'signal', gradient: 'linear-gradient(135deg, #ffc107, #ffca28)' };
        if (download >= 5) return { label: 'Regular', color: '#ff9800', icon: 'alert-triangle', gradient: 'linear-gradient(135deg, #ff9800, #ffb74d)' };
        return { label: 'Lenta', color: '#ff5252', icon: 'wifi-off', gradient: 'linear-gradient(135deg, #ff5252, #ff867c)' };
    }
    
    // Rating reactivo
    $: currentRating = lastResult ? getSpeedRating(lastResult.download_mbps) : null;
</script>

<div class="speedtest-card" class:compact class:testing class:has-results={lastResult && stage === 'complete'}>
    <!-- Matrix Background Effect -->
    <div class="matrix-bg">
        <div class="matrix-grid"></div>
        {#if testing}
            <div class="matrix-pulse"></div>
            <div class="matrix-pulse delay-1"></div>
            <div class="matrix-pulse delay-2"></div>
        {/if}
    </div>
    
    {#if !compact}
        <div class="card-header">
            <div class="header-left">
                <Icon name="gauge" size={18} />
                <h3>Speed Test</h3>
            </div>
            <span class="subtitle">Cloudflare Network Test</span>
        </div>
    {/if}
    
    <!-- Central Action Area -->
    <div class="central-area">
        {#if lastResult && stage === 'complete' && currentRating}
            <!-- Resultados con transición -->
            <div class="results" class:fade-in={!showTransition}>
                <div class="results-grid">
                    <!-- Download -->
                    <div class="speed-card download">
                        <div class="speed-icon-wrap">
                            <Icon name="arrow-down" size={20} />
                        </div>
                        <div class="speed-data">
                            <span class="speed-value">{formatSpeed(lastResult.download_mbps)}</span>
                            <span class="speed-label">Descarga</span>
                        </div>
                    </div>
                    
                    <!-- Central Rating Badge -->
                    <div class="rating-center">
                        <div class="rating-badge" style="--rating-color: {currentRating.color}; --rating-gradient: {currentRating.gradient}">
                            <div class="rating-icon-wrap">
                                <Icon name={currentRating.icon} size={24} color={currentRating.color} />
                            </div>
                            <span class="rating-text">{currentRating.label}</span>
                        </div>
                    </div>
                    
                    <!-- Upload -->
                    <div class="speed-card upload">
                        <div class="speed-icon-wrap upload-icon">
                            <Icon name="arrow-up" size={20} />
                        </div>
                        <div class="speed-data">
                            <span class="speed-value">{formatSpeed(lastResult.upload_mbps)}</span>
                            <span class="speed-label">Subida</span>
                        </div>
                    </div>
                </div>
                
                <!-- Latency metrics -->
                <div class="latency-row">
                    <div class="latency-item">
                        <Icon name="activity" size={14} />
                        <span>{lastResult.ping_ms.toFixed(0)}ms ping</span>
                    </div>
                    <div class="latency-item">
                        <Icon name="bar-chart-2" size={14} />
                        <span>{lastResult.jitter_ms.toFixed(1)}ms jitter</span>
                    </div>
                    <div class="latency-item">
                        <Icon name="clock" size={14} />
                        <span>{formatDate(lastResult.timestamp)}</span>
                    </div>
                </div>
                
                <div class="action-row">
                    <button class="btn btn-glass" on:click={runSpeedTest} disabled={testing}>
                        <Icon name="refresh-cw" size={14} />
                        Probar de nuevo
                    </button>
                    
                    {#if resetCountdown > 0}
                        <div class="reset-countdown">
                            <span class="countdown-text">Reset en {resetCountdown}s</span>
                            <button class="btn-cancel-reset" on:click={cancelAutoReset} title="Mantener resultados">
                                <Icon name="x" size={12} />
                            </button>
                        </div>
                    {/if}
                </div>
            </div>
        {:else if testing}
            <!-- En progreso - Animación Matrix -->
            <div class="testing-view">
                <div class="orbit-container">
                    <div class="orbit-ring ring-1"></div>
                    <div class="orbit-ring ring-2"></div>
                    <div class="orbit-ring ring-3"></div>
                    
                    <div class="center-icon" class:downloading={stage === 'download'} class:uploading={stage === 'upload'}>
                        <Icon name={getStageIcon(stage)} size={32} />
                    </div>
                </div>
                
                <div class="test-info">
                    <span class="stage-text">{getStageLabel(stage)}</span>
                    
                    {#if stage === 'download' || stage === 'upload'}
                        <div class="live-speed">
                            <span class="speed-num">{currentSpeed.toFixed(2)}</span>
                            <span class="speed-unit">Mbps</span>
                        </div>
                    {/if}
                    
                    <div class="progress-track">
                        <div class="progress-glow" style="width: {progress}%"></div>
                        <div class="progress-bar-inner" style="width: {progress}%"></div>
                    </div>
                    
                    <span class="message-text">{message}</span>
                </div>
            </div>
        {:else}
            <!-- Idle - Botón Central Mejorado -->
            <div class="idle-view">
                <button class="start-button" on:click={runSpeedTest}>
                    <div class="button-rings">
                        <div class="ring pulse-ring"></div>
                        <div class="ring pulse-ring delay"></div>
                    </div>
                    <div class="button-core">
                        <!-- Icono de Speedometer/Gauge -->
                        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 2a10 10 0 1 0 10 10" opacity="0.3"/>
                            <path d="M12 2a10 10 0 0 1 10 10"/>
                            <path d="M12 6v2" opacity="0.6"/>
                            <path d="M6.34 7.34l1.42 1.42" opacity="0.6"/>
                            <path d="M6 12h2" opacity="0.6"/>
                            <circle cx="12" cy="12" r="2" fill="currentColor"/>
                            <path d="M12 12l4-4" stroke-width="2.5"/>
                        </svg>
                    </div>
                </button>
                <span class="start-label">Medir Velocidad</span>
                <button class="server-selector-btn" on:click={() => showServerSelect = true}>
                    <Icon name="server" size={12} />
                    {SERVERS.find(s => s.id === selectedServer)?.name || 'Cloudflare'}
                    <Icon name="chevron-down" size={12} />
                </button>
            </div>
        {/if}
    </div>
    
    <!-- Server Selector Modal -->
    {#if showServerSelect}
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div class="modal-overlay" on:click={() => showServerSelect = false}>
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div class="server-modal" on:click|stopPropagation>
                <div class="modal-header">
                    <h4><Icon name="server" size={16} /> Seleccionar Servidor</h4>
                    <button class="modal-close" on:click={() => showServerSelect = false}>
                        <Icon name="x" size={18} />
                    </button>
                </div>
                <div class="server-list">
                    {#each SERVERS as server}
                        <button 
                            class="server-option"
                            class:selected={selectedServer === server.id}
                            class:default={server.default}
                            on:click={() => selectServer(server.id)}
                        >
                            <div class="server-info">
                                <span class="server-name">
                                    {server.name}
                                    {#if server.default}
                                        <span class="default-badge">Recomendado</span>
                                    {/if}
                                </span>
                                <span class="server-desc">{server.desc}</span>
                            </div>
                            {#if selectedServer === server.id}
                                <Icon name="check" size={16} color="#00d4aa" />
                            {/if}
                        </button>
                    {/each}
                </div>
                {#if selectedServer === 'custom'}
                    <div class="custom-url">
                        <label for="customServerUrl">URL del servidor:</label>
                        <input 
                            id="customServerUrl"
                            type="text" 
                            bind:value={customServerUrl} 
                            placeholder="https://..."
                        />
                    </div>
                {/if}
                <div class="modal-footer">
                    <p class="modal-hint">
                        <Icon name="info" size={12} />
                        Cloudflare es recomendado por su red global de edge servers
                    </p>
                </div>
            </div>
        </div>
    {/if}
</div>

<style>
    .speedtest-card {
        position: relative;
        background: rgba(26, 26, 26, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
        min-height: 500px;
        height: auto;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .speedtest-card:hover {
        border-color: rgba(0, 212, 170, 0.2);
    }
    
    .speedtest-card.testing {
        border-color: rgba(0, 212, 170, 0.3);
        box-shadow: 0 0 30px rgba(0, 212, 170, 0.1);
    }
    
    .speedtest-card.compact {
        padding: 1rem;
        min-height: 420px;
    }
    
    /* Matrix Background */
    .matrix-bg {
        position: absolute;
        inset: 0;
        overflow: hidden;
        pointer-events: none;
        z-index: 0;
    }
    
    .matrix-grid {
        position: absolute;
        inset: 0;
        background-image: 
            linear-gradient(rgba(0, 212, 170, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 212, 170, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
        opacity: 0.5;
    }
    
    .matrix-pulse {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        border: 2px solid rgba(0, 212, 170, 0.3);
        transform: translate(-50%, -50%);
        animation: matrixPulse 2s ease-out infinite;
    }
    
    .matrix-pulse.delay-1 { animation-delay: 0.5s; }
    .matrix-pulse.delay-2 { animation-delay: 1s; }
    
    @keyframes matrixPulse {
        0% {
            width: 60px;
            height: 60px;
            opacity: 0.8;
        }
        100% {
            width: 400px;
            height: 400px;
            opacity: 0;
        }
    }
    
    /* Header */
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        z-index: 1;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--primary, #00d4aa);
    }
    
    .card-header h3 {
        font-size: 1rem;
        font-weight: 600;
        margin: 0;
        color: var(--text-primary, #fff);
    }
    
    .subtitle {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        background: rgba(0, 212, 170, 0.1);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    
    /* Central Area */
    .central-area {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        z-index: 1;
        min-height: 350px;
    }
    
    /* ========== IDLE VIEW ========== */
    .idle-view {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 1rem 0;
    }
    
    .start-button {
        position: relative;
        width: 100px;
        height: 100px;
        border: none;
        background: transparent;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .start-button:hover {
        transform: scale(1.05);
    }
    
    .start-button:hover .button-core {
        background: linear-gradient(135deg, #00e6b8, #00d4aa);
        box-shadow: 0 0 30px rgba(0, 212, 170, 0.5);
    }
    
    .button-rings {
        position: absolute;
        inset: 0;
    }
    
    .ring {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 2px solid rgba(0, 212, 170, 0.4);
    }
    
    .pulse-ring {
        animation: ringPulse 2s ease-out infinite;
    }
    
    .pulse-ring.delay {
        animation-delay: 1s;
    }
    
    @keyframes ringPulse {
        0% {
            transform: scale(1);
            opacity: 0.6;
        }
        100% {
            transform: scale(1.8);
            opacity: 0;
        }
    }
    
    .button-core {
        position: absolute;
        inset: 12px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00d4aa 0%, #00e5b8 50%, #00f5c4 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0a0a0a;
        box-shadow: 
            0 0 30px rgba(0, 212, 170, 0.5),
            0 4px 15px rgba(0, 0, 0, 0.3),
            inset 0 2px 15px rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .button-core svg {
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }
    
    .start-label {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* ========== TESTING VIEW ========== */
    .testing-view {
        display: flex;
        align-items: center;
        gap: 2rem;
        width: 100%;
        padding: 0 1rem;
    }
    
    .orbit-container {
        position: relative;
        width: 100px;
        height: 100px;
        flex-shrink: 0;
    }
    
    .orbit-ring {
        position: absolute;
        border-radius: 50%;
        border: 1px solid rgba(0, 212, 170, 0.2);
    }
    
    .ring-1 {
        inset: 0;
        animation: orbitSpin 3s linear infinite;
    }
    
    .ring-2 {
        inset: 10px;
        animation: orbitSpin 2s linear infinite reverse;
        border-color: rgba(0, 212, 170, 0.3);
    }
    
    .ring-3 {
        inset: 20px;
        animation: orbitSpin 1.5s linear infinite;
        border-color: rgba(0, 212, 170, 0.4);
    }
    
    @keyframes orbitSpin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .center-icon {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(0, 212, 170, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary, #00d4aa);
        animation: iconPulse 1s ease-in-out infinite;
    }
    
    .center-icon.downloading {
        color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.15);
    }
    
    .center-icon.uploading {
        color: #9C27B0;
        background: rgba(156, 39, 176, 0.15);
    }
    
    @keyframes iconPulse {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-50%, -50%) scale(1.1); }
    }
    
    .test-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .stage-text {
        font-size: 0.8rem;
        color: var(--text-secondary, #a0a0a0);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .live-speed {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
    }
    
    .speed-num {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary, #00d4aa);
        font-family: 'JetBrains Mono', monospace;
        line-height: 1;
    }
    
    .speed-unit {
        font-size: 0.875rem;
        color: var(--text-muted, #666);
    }
    
    .progress-track {
        position: relative;
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-glow {
        position: absolute;
        top: -2px;
        left: 0;
        height: 10px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.5), transparent);
        filter: blur(4px);
        transition: width 0.3s ease;
    }
    
    .progress-bar-inner {
        height: 100%;
        background: linear-gradient(90deg, var(--primary, #00d4aa), #00e6b8);
        border-radius: 3px;
        transition: width 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 212, 170, 0.5);
    }
    
    .message-text {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    /* ========== RESULTS VIEW ========== */
    .results {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        width: 100%;
        opacity: 0;
        animation: fadeIn 0.5s ease forwards;
    }
    
    .results.fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .results-grid {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        gap: 1.5rem;
        align-items: center;
        width: 100%;
    }
    
    .speed-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .speed-icon-wrap {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(0, 212, 170, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary, #00d4aa);
    }
    
    .speed-icon-wrap.upload-icon {
        background: rgba(156, 39, 176, 0.15);
        color: #9C27B0;
    }
    
    .speed-data {
        display: flex;
        flex-direction: column;
    }
    
    .speed-value {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.2;
    }
    
    .speed-label {
        font-size: 0.65rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .rating-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
    }
    
    .rating-badge {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 1.5rem;
        background: rgba(0, 0, 0, 0.4);
        border: 2px solid var(--rating-color);
        border-radius: 16px;
        box-shadow: 
            0 4px 20px rgba(0, 0, 0, 0.3),
            0 0 30px color-mix(in srgb, var(--rating-color) 20%, transparent),
            inset 0 0 20px color-mix(in srgb, var(--rating-color) 10%, transparent);
        animation: ratingPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    @keyframes ratingPop {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .rating-icon-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--rating-gradient);
        box-shadow: 0 0 20px color-mix(in srgb, var(--rating-color) 50%, transparent);
    }
    
    .rating-icon-wrap :global(svg) {
        color: #000 !important;
    }
    
    .rating-text {
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--rating-color);
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .latency-row {
        display: flex;
        gap: 1.5rem;
        justify-content: center;
    }
    
    .latency-item {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    /* Glass Button */
    .btn-glass {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-glass:hover:not(:disabled) {
        background: rgba(0, 212, 170, 0.15);
        border-color: rgba(0, 212, 170, 0.3);
        color: var(--primary, #00d4aa);
    }
    
    .btn-glass:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* Action Row con countdown */
    .action-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .reset-countdown {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .countdown-text {
        font-variant-numeric: tabular-nums;
    }
    
    .btn-cancel-reset {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        padding: 0;
        background: rgba(255, 255, 255, 0.1);
        border: none;
        border-radius: 50%;
        color: var(--text-muted, #666);
        cursor: pointer;
        transition: all 0.15s ease;
    }
    
    .btn-cancel-reset:hover {
        background: rgba(255, 82, 82, 0.2);
        color: var(--error, #ff5252);
    }

    /* Server Selector Button */
    .server-selector-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-top: 0.5rem;
    }
    
    .server-selector-btn:hover {
        background: rgba(0, 212, 170, 0.15);
        border-color: rgba(0, 212, 170, 0.4);
        color: var(--primary, #00d4aa);
        transform: translateY(-1px);
    }
    
    /* Modal Overlay */
    .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 100;
        animation: fadeIn 0.2s ease;
    }
    
    /* Server Modal */
    .server-modal {
        background: rgba(30, 30, 30, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        width: 90%;
        max-width: 400px;
        overflow: hidden;
        animation: slideUp 0.3s ease;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .modal-header h4 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        font-size: 0.95rem;
        color: var(--text-primary, #fff);
    }
    
    .modal-close {
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        cursor: pointer;
        padding: 0.25rem;
        display: flex;
        transition: color 0.2s;
    }
    
    .modal-close:hover {
        color: var(--text-primary, #fff);
    }
    
    .server-list {
        padding: 0.5rem;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        max-height: 300px;
        overflow-y: auto;
    }
    
    .server-option {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1rem;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
    }
    
    .server-option:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    .server-option.selected {
        background: rgba(0, 212, 170, 0.1);
        border-color: rgba(0, 212, 170, 0.3);
    }
    
    .server-info {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    
    .server-name {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--text-primary, #fff);
    }
    
    .default-badge {
        font-size: 0.6rem;
        padding: 0.15rem 0.4rem;
        background: rgba(0, 212, 170, 0.2);
        color: var(--primary, #00d4aa);
        border-radius: 4px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .server-desc {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .custom-url {
        padding: 0.75rem 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .custom-url label {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin-bottom: 0.4rem;
    }
    
    .custom-url input {
        width: 100%;
        padding: 0.5rem 0.75rem;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        color: var(--text-primary, #fff);
        font-size: 0.8rem;
    }
    
    .custom-url input:focus {
        outline: none;
        border-color: rgba(0, 212, 170, 0.5);
    }
    
    .modal-footer {
        padding: 0.75rem 1rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .modal-hint {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
</style>
