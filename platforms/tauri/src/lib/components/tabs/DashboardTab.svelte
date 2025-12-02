<!--
    DashboardTab.svelte - Tab modular de Dashboard
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { invoke, isTauriAvailable } from '$lib/tauri-bridge';
    import StatCard from '../StatCard.svelte';
    import DiagnosticChain from '../DiagnosticChain.svelte';
    import DiagnosticHistory from '../DiagnosticHistory.svelte';
    import AlgorithmChart from '../AlgorithmChart.svelte';
    import SkeletonCard from '../SkeletonCard.svelte';
    import SpeedTestCard from '../SpeedTestCard.svelte';
    import OptimizationProfiles from '../OptimizationProfiles.svelte';
    import DNSManager from '../DNSManager.svelte';
    import Icon from '../Icon.svelte';
    import { diagnosticHistory, calculateHealthScore, type DiagnosticReport } from '$lib/stores/diagnosticStore';
    import type { TcpSettings, DNSConfig } from '$lib/types';
    
    export let loading = false;
    export let adapters: any[] = [];
    export let selectedAdapter = '';
    export let diagnostic: any = null;
    export let diagnosing = false;
    export let downloadRate = 0;
    export let uploadRate = 0;
    export let latency = 0;
    export let uptime = 0;
    
    const dispatch = createEventDispatcher();
    
    // Detectar si estamos en Tauri o web
    let isTauri = false;
    
    // Estado del protocolo y DNS
    let tcpSettings: TcpSettings | null = null;
    let dnsConfig: DNSConfig | null = null;
    let detectedProfile: 'Conservative' | 'Balanced' | 'Aggressive' | 'Unoptimized' | 'Custom' = 'Unoptimized';
    let loadingProtocol = true;
    let protocolError: string | null = null;
    let dnsError: string | null = null;
    
    // Speed Test result
    let speedTestResult: { download_mbps: number; upload_mbps: number; ping_ms: number } | null = null;
    
    // Optimization state
    let optimizing = false;
    let dryRunMode = false;
    
    // DNS state
    let autoFailoverEnabled = false;
    
    // Tooltip activo
    let activeTooltip: string | null = null;
    
    // Mapeo de DNS conocidos
    const DNS_PROVIDERS: Record<string, { name: string; icon: string; tier: number }> = {
        '1.1.1.1': { name: 'Cloudflare', icon: '☁️', tier: 1 },
        '1.0.0.1': { name: 'Cloudflare', icon: '☁️', tier: 1 },
        '8.8.8.8': { name: 'Google', icon: '🔍', tier: 2 },
        '8.8.4.4': { name: 'Google', icon: '🔍', tier: 2 },
        '9.9.9.9': { name: 'Quad9', icon: '🛡️', tier: 3 },
        '149.112.112.112': { name: 'Quad9', icon: '🛡️', tier: 3 },
        '208.67.222.222': { name: 'OpenDNS', icon: '🔐', tier: 4 },
        '208.67.220.220': { name: 'OpenDNS', icon: '🔐', tier: 4 },
        '94.140.14.14': { name: 'AdGuard', icon: '🚫', tier: 5 },
        '94.140.15.15': { name: 'AdGuard', icon: '🚫', tier: 5 },
        '185.228.168.9': { name: 'CleanBrowsing', icon: '🧹', tier: 6 },
    };
    
    // Información COMPLETA de optimizaciones con tooltips detallados
    const TCP_INFO: Record<string, { 
        label: string; 
        docPath: string; 
        shortDesc: string;
        fullDesc: string;
        impact: 'high' | 'medium' | 'low';
        profiles: string[]; // En qué perfiles está incluido
    }> = {
        // Configuración Base
        rss: { 
            label: 'RSS', 
            docPath: 'tcp-core', 
            shortDesc: 'Multi-CPU para paquetes',
            fullDesc: 'Receive Side Scaling distribuye el procesamiento de paquetes entre múltiples núcleos de CPU. Mejora el rendimiento en conexiones de alta velocidad.',
            impact: 'high',
            profiles: ['Conservative', 'Balanced', 'Aggressive']
        },
        rsc: { 
            label: 'RSC', 
            docPath: 'tcp-core', 
            shortDesc: 'Combina segmentos TCP',
            fullDesc: 'Receive Segment Coalescing agrupa múltiples segmentos TCP pequeños en uno más grande, reduciendo interrupciones de CPU.',
            impact: 'medium',
            profiles: ['Conservative', 'Balanced', 'Aggressive']
        },
        autotuning: { 
            label: 'Autotuning', 
            docPath: 'tcp-core', 
            shortDesc: 'Buffers dinámicos TCP',
            fullDesc: 'Ajusta automáticamente el tamaño del buffer de recepción. "normal" es seguro, "experimental" permite buffers más grandes para conexiones rápidas.',
            impact: 'high',
            profiles: ['Conservative', 'Balanced', 'Aggressive']
        },
        ecn: { 
            label: 'ECN', 
            docPath: 'tcp-congestion-control', 
            shortDesc: 'Notificación de congestión',
            fullDesc: 'Explicit Congestion Notification permite a los routers señalar congestión SIN descartar paquetes. Reduce retransmisiones.',
            impact: 'medium',
            profiles: ['Balanced', 'Aggressive']
        },
        timestamps: { 
            label: 'Timestamps', 
            docPath: 'tcp-core', 
            shortDesc: 'Mejor cálculo de RTT',
            fullDesc: 'RFC 1323 Timestamps permiten calcular el Round-Trip Time con mayor precisión, mejorando el control de congestión.',
            impact: 'low',
            profiles: ['Aggressive']
        },
        congestion_provider: { 
            label: 'Algoritmo', 
            docPath: 'bbr-vs-cubic', 
            shortDesc: 'Control de congestión',
            fullDesc: 'Windows usa CUBIC (estándar). Linux puede usar BBR. CUBIC es loss-based, BBR es model-based. Ambos funcionan bien.',
            impact: 'high',
            profiles: ['Conservative', 'Balanced', 'Aggressive']
        },
        // Optimizaciones Avanzadas
        fast_open: { 
            label: 'Fast Open', 
            docPath: 'tcp-core', 
            shortDesc: 'Datos en handshake',
            fullDesc: 'TCP Fast Open (TFO) envía datos en el paquete SYN inicial, ahorrando 1 RTT en conexiones repetidas. Requiere soporte del servidor.',
            impact: 'medium',
            profiles: ['Aggressive']
        },
        hystart: { 
            label: 'HyStart++', 
            docPath: 'tcp-congestion-control', 
            shortDesc: 'Slow-start inteligente',
            fullDesc: 'Hybrid Slow Start detecta cuando salir del slow-start antes de causar pérdidas. Evita queue buildup similar a BBR.',
            impact: 'medium',
            profiles: ['Balanced', 'Aggressive']
        },
        prr: { 
            label: 'PRR', 
            docPath: 'tcp-congestion-control', 
            shortDesc: 'Recuperación suave',
            fullDesc: 'Proportional Rate Reduction recupera la velocidad gradualmente tras pérdidas, en lugar de reducir bruscamente a la mitad.',
            impact: 'medium',
            profiles: ['Balanced', 'Aggressive']
        },
        pacing: { 
            label: 'Pacing', 
            docPath: 'tcp-congestion-control', 
            shortDesc: 'Envío uniforme',
            fullDesc: 'Envía paquetes de forma uniforme en el tiempo en lugar de ráfagas. Reduce buffer bloat y mejora latencia. Técnica clave de BBR.',
            impact: 'high',
            profiles: ['Aggressive']
        },
        initial_rto: { 
            label: 'Initial RTO', 
            docPath: 'tcp-core', 
            shortDesc: 'Timeout inicial',
            fullDesc: 'Retransmission Timeout inicial. El default es 3 segundos. Reducirlo a 1s acelera la detección de pérdidas pero puede causar retransmisiones innecesarias.',
            impact: 'low',
            profiles: ['Aggressive']
        },
        rack: { 
            label: 'RACK', 
            docPath: 'tcp-congestion-control', 
            shortDesc: 'Detección de pérdidas',
            fullDesc: 'Recent ACK usa timestamps para detectar pérdidas más rápido que el tradicional triple-duplicate ACK.',
            impact: 'medium',
            profiles: ['Aggressive']
        },
    };
    
    // Categorizar para mostrar
    const basicKeys = ['rss', 'rsc', 'autotuning', 'ecn', 'timestamps', 'congestion_provider'];
    const advancedKeys = ['fast_open', 'hystart', 'prr', 'pacing', 'initial_rto', 'rack'];
    
    onMount(async () => {
        isTauri = isTauriAvailable();
        await loadProtocolInfo();
    });
    
    async function loadProtocolInfo() {
        loadingProtocol = true;
        protocolError = null;
        dnsError = null;
        
        try {
            tcpSettings = await invoke<TcpSettings>('get_current_settings');
            detectedProfile = detectProfile(tcpSettings);
        } catch (e) {
            console.error('Error cargando protocolo TCP:', e);
            protocolError = String(e);
        }
        
        const adapterToUse = selectedAdapter || (adapters.length > 0 ? adapters[0].name : '');
        if (adapterToUse) {
            try {
                dnsConfig = await invoke<DNSConfig>('get_current_dns', { adapter: adapterToUse });
            } catch (e) {
                console.warn('No se pudo cargar DNS config:', e);
                dnsError = String(e);
            }
        }
        
        loadingProtocol = false;
    }
    
    function detectProfile(settings: any): 'Conservative' | 'Balanced' | 'Aggressive' | 'Unoptimized' | 'Custom' {
        if (!settings) return 'Unoptimized';
        
        const checks = {
            rss: settings.rss?.toLowerCase().includes('enabled'),
            rsc: settings.rsc?.toLowerCase().includes('enabled'),
            autotuning: settings.autotuning?.toLowerCase().includes('normal') || settings.autotuning?.toLowerCase().includes('experimental'),
            ecn: settings.ecn?.toLowerCase().includes('enabled'),
            timestamps: settings.timestamps?.toLowerCase().includes('enabled'),
            fast_open: settings.fast_open?.toLowerCase().includes('enabled'),
            hystart: settings.hystart?.toLowerCase().includes('enabled'),
            prr: settings.prr?.toLowerCase().includes('enabled'),
            pacing: settings.pacing?.toLowerCase().includes('always'),
        };
        
        // Contar por categoría
        const basicCount = [checks.rss, checks.rsc, checks.autotuning].filter(Boolean).length;
        const balancedCount = [checks.ecn, checks.hystart, checks.prr].filter(Boolean).length;
        const aggressiveCount = [checks.fast_open, checks.pacing, checks.timestamps].filter(Boolean).length;
        
        // Aggressive: todo habilitado
        if (basicCount === 3 && balancedCount >= 2 && aggressiveCount >= 2) {
            return 'Aggressive';
        }
        
        // Balanced: básicos + ECN/HyStart/PRR
        if (basicCount === 3 && balancedCount >= 2) {
            return 'Balanced';
        }
        
        // Conservative: solo básicos
        if (basicCount === 3) {
            return 'Conservative';
        }
        
        // Algo configurado pero no coincide con perfil
        if (basicCount > 0 || balancedCount > 0 || aggressiveCount > 0) {
            return 'Custom';
        }
        
        return 'Unoptimized';
    }
    
    function getDnsProvider(server: string): { name: string; icon: string; tier: number } {
        const known = DNS_PROVIDERS[server];
        if (known) return known;
        if (server.startsWith('192.168.') || server.startsWith('10.') || server.startsWith('172.')) {
            return { name: 'Router/Local', icon: '🏠', tier: 7 };
        }
        return { name: 'ISP/Custom', icon: '🌐', tier: 8 };
    }
    
    function getProfileInfo(profile: string): { color: string; icon: string; action: string } {
        const info: Record<string, { color: string; icon: string; action: string }> = {
            'Conservative': { color: '#4CAF50', icon: '🟢', action: 'Ya tienes optimizaciones básicas' },
            'Balanced': { color: '#FFC107', icon: '🟡', action: 'Puedes mejorar a Agresivo' },
            'Aggressive': { color: '#F44336', icon: '🔴', action: '¡Máximo rendimiento!' },
            'Unoptimized': { color: '#9E9E9E', icon: '⚪', action: 'Ir a optimizar →' },
            'Custom': { color: '#9C27B0', icon: '🟣', action: 'Configuración personalizada' },
        };
        return info[profile] || info['Unoptimized'];
    }
    
    function formatUptime(s: number): string {
        const h = Math.floor(s / 3600);
        const m = Math.floor((s % 3600) / 60);
        const sec = s % 60;
        return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${sec.toString().padStart(2,'0')}`;
    }
    
    function goToOptimize() {
        dispatch('navigate', { tab: 'optimize' });
    }
    
    function goToDocsSection(section: string) {
        dispatch('navigate', { tab: 'docs', section });
    }
    
    async function handleApplyProfile(event: CustomEvent<string>) {
        const profile = event.detail;
        optimizing = true;
        
        try {
            if (dryRunMode) {
                // En modo dry-run, mostrar info
                dispatch('showNotification', { 
                    type: 'info', 
                    message: `Modo simulación: el perfil "${profile}" no se aplicará` 
                });
            } else {
                // El comando espera el enum: Conservative, Balanced, Aggressive
                const result = await invoke<string[]>('apply_profile', { profile });
                await loadProtocolInfo(); // Recargar estado
                const count = result?.length || 0;
                dispatch('showNotification', { 
                    type: 'success', 
                    message: `Perfil "${profile}" aplicado (${count} optimizaciones)` 
                });
            }
        } catch (e) {
            console.error('Error aplicando perfil:', e);
            dispatch('showNotification', { 
                type: 'error', 
                message: `Error: ${e}` 
            });
        } finally {
            optimizing = false;
        }
    }
    
    function handleToggleDryRun() {
        dryRunMode = !dryRunMode;
    }
    
    async function handleResetSettings() {
        optimizing = true;
        try {
            await invoke('reset_to_defaults');
            await loadProtocolInfo();
            dispatch('showNotification', { 
                type: 'success', 
                message: 'Configuración TCP restaurada a valores por defecto' 
            });
        } catch (e) {
            console.error('Error restaurando configuración:', e);
            dispatch('showNotification', { 
                type: 'error', 
                message: `Error: ${e}` 
            });
        } finally {
            optimizing = false;
        }
    }
    
    function handleDNSChange(event: CustomEvent<{ dns: string[]; dhcp?: boolean }>) {
        const { dns, dhcp } = event.detail;
        if (dhcp) {
            dispatch('showNotification', { type: 'success', message: 'DNS restaurado a DHCP' });
        } else if (dns.length > 0) {
            dispatch('showNotification', { type: 'success', message: `DNS configurado: ${dns[0]}` });
        }
        // Recargar la info del protocolo para actualizar el estado
        loadProtocolInfo();
    }
    
    function getTcpValue(key: string): string {
        if (!tcpSettings) return 'N/A';
        const val = (tcpSettings as any)[key];
        if (val === null || val === undefined) return 'N/A';
        if (key === 'initial_rto' && typeof val === 'number') return `${val}ms`;
        return String(val);
    }
    
    function isEnabled(key: string): boolean {
        const val = getTcpValue(key).toLowerCase();
        return val.includes('enabled') || val === 'normal' || val === 'experimental' || val === 'always' || val === 'cubic';
    }
    
    function showTooltip(key: string) { activeTooltip = key; }
    function hideTooltip() { activeTooltip = null; }
    
    function safeValue(val: any, fallback: string = 'N/A'): string {
        if (val === null || val === undefined || val === '') return fallback;
        return String(val);
    }
    
    // Toggle para mostrar/ocultar gráficas de algoritmos
    let showAlgorithmCharts = false;
    
    // Manejar evento de diagnóstico completado para guardar en historial
    function handleDiagnosticComplete(result: any) {
        if (!result) return;
        
        // Calcular health score basado en resultados
        const partialReport = {
            adapterOk: result.adapter_check?.success ?? true,
            routerOk: result.router_check?.success ?? true,
            routerLatencyMs: result.router_check?.latency_ms || 0,
            ispOk: result.isp_check?.success ?? true,
            ispLatencyMs: result.isp_check?.latency_ms || 0,
            dnsOk: result.dns_check?.success ?? true,
            dnsLatencyMs: result.dns_check?.latency_ms || 0,
        };
        
        const { score, status } = calculateHealthScore(partialReport);
        
        const report: Omit<DiagnosticReport, 'id' | 'timestamp' | 'appVersion'> = {
            type: 'full',
            health: status,
            healthScore: score,
            failurePoint: result.failure_point || 'none',
            // Fases
            adapterOk: partialReport.adapterOk,
            adapterName: selectedAdapter || 'Unknown',
            routerOk: partialReport.routerOk,
            routerLatencyMs: partialReport.routerLatencyMs,
            ispOk: partialReport.ispOk,
            ispLatencyMs: partialReport.ispLatencyMs,
            dnsOk: partialReport.dnsOk,
            dnsLatencyMs: partialReport.dnsLatencyMs,
            // Metadata
            recommendation: result.recommendation || '',
            selectedAdapter: selectedAdapter,
            dnsServers: dnsConfig?.servers || [],
        };
        
        diagnosticHistory.add(report);
    }
    
    function handleViewDiagnosticDetails(event: CustomEvent<DiagnosticReport>) {
        // Por ahora mostramos en consola, luego modal
        console.log('Ver detalles:', event.detail);
    }
    
    function handleViewAllDiagnostics() {
        dispatch('navigate', { tab: 'reports' });
    }
    
    // Exponer función para que el padre pueda guardar diagnósticos
    export function saveDiagnostic(result: any) {
        handleDiagnosticComplete(result);
    }
    
    $: if (selectedAdapter) { loadProtocolInfo(); }
</script>

<div class="dashboard">
    <!-- Métricas en Tiempo Real + Speed Test -->
    <div class="metrics-section">
        <!-- Tráfico en Vivo -->
        <section class="card live-traffic">
            <div class="card-header">
                <h2>📊 Tráfico en Vivo</h2>
                <span class="live-indicator">
                    <span class="pulse-dot"></span>
                    Monitoreando
                </span>
            </div>
            <div class="stats-grid">
                {#if loading}
                    {#each [1,2,3,4] as _}
                        <SkeletonCard variant="stat" />
                    {/each}
                {:else}
                    <StatCard icon="📥" label="Descarga" value={downloadRate.toFixed(2)} unit="Mbps" variant="primary" />
                    <StatCard icon="📤" label="Subida" value={uploadRate.toFixed(2)} unit="Mbps" variant="success" />
                    <StatCard icon="🏓" label="Latencia" value={latency.toFixed(0)} unit="ms" variant={latency > 100 ? 'warning' : 'default'} />
                    <StatCard icon="⏱️" label="Uptime" value={formatUptime(uptime)} variant="default" />
                {/if}
            </div>
            <p class="traffic-hint">
                💡 Estas son las métricas de tráfico actual. Para medir tu velocidad máxima, usa el Speed Test.
            </p>
        </section>
        
        <!-- Speed Test -->
        <section class="card speedtest-section">
            <SpeedTestCard 
                on:complete={(e) => {
                    speedTestResult = e.detail;
                    // Integrar con diagnóstico
                    dispatch('speedTestComplete', e.detail);
                }}
            />
        </section>
    </div>
    
    <!-- Quick Optimization Profiles -->
    <section class="quick-optimization">
        <OptimizationProfiles 
            loading={loadingProtocol}
            {optimizing}
            {tcpSettings}
            {dryRunMode}
            compact={true}
            showSettings={false}
            showReset={false}
            on:applyProfile={handleApplyProfile}
            on:toggleDryRun={handleToggleDryRun}
            on:reset={handleResetSettings}
        />
    </section>
    
    <!-- Protocol Status & DNS Summary -->
    <div class="info-grid">
        <!-- TCP Protocol Status -->
        <section class="card protocol-card">
            <div class="card-header">
                <h2>⚙️ Configuración de Red</h2>
                <div class="header-actions">
                    <button class="doc-link-btn" on:click={() => goToDocsSection('tcp-congestion-control')} title="Ver documentación">
                        <Icon name="book-open" size={14} />
                    </button>
                    {#if detectedProfile !== 'Aggressive'}
                        <button class="btn btn-sm btn-accent" on:click={goToOptimize}>
                            ⚡ Optimizar
                        </button>
                    {/if}
                </div>
            </div>
            
            <!-- Aviso de modo web -->
            {#if !isTauri}
                <div class="web-mode-notice">
                    <Icon name="info" size={16} />
                    <span>Modo desarrollo - Los datos mostrados son de demostración. Ejecuta la app Tauri para ver tu configuración real.</span>
                </div>
            {/if}
            
            {#if loadingProtocol}
                <div class="loading-mini">
                    <span class="spinner-mini"></span>
                    Leyendo configuración del sistema...
                </div>
            {:else if protocolError}
                <div class="error-mini">
                    <Icon name="alert-triangle" size={20} />
                    <span>Error: {protocolError}</span>
                    <button class="btn btn-sm" on:click={loadProtocolInfo}>Reintentar</button>
                </div>
            {:else if tcpSettings}
                <!-- Perfil detectado con acción -->
                <div class="protocol-header">
                    <div class="detected-profile" style="--profile-color: {getProfileInfo(detectedProfile).color}">
                        <span class="profile-icon">{getProfileInfo(detectedProfile).icon}</span>
                        <span class="profile-name">{detectedProfile}</span>
                    </div>
                    <span class="profile-action">{getProfileInfo(detectedProfile).action}</span>
                </div>
                
                <!-- Configuración Base -->
                <div class="settings-section">
                    <h4 class="section-title">📊 Configuración Base</h4>
                    <div class="tcp-settings-grid">
                        {#each basicKeys as key}
                            {@const info = TCP_INFO[key]}
                            <div 
                                class="tcp-setting" 
                                class:enabled={isEnabled(key)}
                                on:mouseenter={() => showTooltip(key)}
                                on:mouseleave={hideTooltip}
                                role="button"
                                tabindex="0"
                            >
                                <div class="setting-header">
                                    <span class="setting-label">{info.label}</span>
                                    <button 
                                        class="info-btn" 
                                        on:click|stopPropagation={() => goToDocsSection(info.docPath)}
                                        title="Ver documentación"
                                    >
                                        <Icon name="help-circle" size={12} />
                                    </button>
                                </div>
                                <span class="setting-value" class:enabled={isEnabled(key)}>
                                    {getTcpValue(key)}
                                </span>
                                <span class="setting-short-desc">{info.shortDesc}</span>
                                
                                <!-- Tooltip -->
                                {#if activeTooltip === key}
                                    <div class="tooltip">
                                        <strong>{info.label}</strong>
                                        <p>{info.fullDesc}</p>
                                        <div class="tooltip-meta">
                                            <span class="impact impact-{info.impact}">Impacto: {info.impact}</span>
                                            <span class="profiles">En: {info.profiles.join(', ')}</span>
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                </div>
                
                <!-- Optimizaciones Avanzadas -->
                <div class="settings-section advanced">
                    <h4 class="section-title">
                        ⚡ Optimizaciones Avanzadas
                        <span class="section-hint" title="Técnicas similares a BBR de Linux, adaptadas para Windows">
                            <Icon name="info" size={12} />
                        </span>
                    </h4>
                    <p class="section-note">
                        Técnicas inspiradas en BBR de Linux. Windows usa CUBIC como algoritmo base, pero estas optimizaciones aplican principios similares.
                    </p>
                    <div class="tcp-settings-grid compact">
                        {#each advancedKeys as key}
                            {@const info = TCP_INFO[key]}
                            <div 
                                class="tcp-setting mini" 
                                class:enabled={isEnabled(key)}
                                on:mouseenter={() => showTooltip(key)}
                                on:mouseleave={hideTooltip}
                                role="button"
                                tabindex="0"
                            >
                                <div class="setting-header">
                                    <span class="setting-label">{info.label}</span>
                                </div>
                                <span class="setting-value mini" class:enabled={isEnabled(key)}>
                                    {getTcpValue(key)}
                                </span>
                                
                                {#if activeTooltip === key}
                                    <div class="tooltip compact">
                                        <strong>{info.label}</strong>
                                        <p>{info.fullDesc}</p>
                                    </div>
                                {/if}
                            </div>
                        {/each}
                    </div>
                </div>
            {:else}
                <div class="empty-mini">No se pudo cargar configuración TCP</div>
            {/if}
        </section>
        
        <!-- DNS Manager -->
        <section class="dns-section">
            <DNSManager 
                adapter={selectedAdapter}
                compact={false}
                autoFailoverEnabled={autoFailoverEnabled}
                on:change={handleDNSChange}
                on:error={(e) => dispatch('showNotification', { type: 'error', message: e.detail })}
                on:flush={() => dispatch('showNotification', { type: 'success', message: 'Caché DNS limpiada' })}
                on:toggleFailover={() => { autoFailoverEnabled = !autoFailoverEnabled; }}
                on:detectFailover={(e) => { 
                    autoFailoverEnabled = e.detail.enabled;
                    dispatch('showNotification', { 
                        type: 'info', 
                        message: `Detectado: ${e.detail.count} DNS configurados - Auto-failover activado` 
                    });
                }}
                on:openFullDNS={() => dispatch('navigate', { tab: 'dns' })}
            />
        </section>
    </div>
    
    <!-- Adapters -->
    <section class="card">
        <h2>📡 Adaptadores de Red</h2>
        {#if loading}
            <div class="adapter-grid">
                {#each [1,2] as _}
                    <SkeletonCard variant="adapter" />
                {/each}
            </div>
        {:else if adapters.length === 0}
            <p class="empty-state">No se encontraron adaptadores activos</p>
        {:else}
            <div class="adapter-grid">
                {#each adapters as adapter}
                    <div class="adapter-card" class:selected={adapter.name === selectedAdapter}>
                        <div class="adapter-header">
                            <h3>{safeValue(adapter.name, 'Adaptador')}</h3>
                            <span class="status-badge up">Up</span>
                        </div>
                        <p class="adapter-desc">{safeValue(adapter.description, 'Sin descripción')}</p>
                        <div class="adapter-stats">
                            <span>🔗 {safeValue(adapter.link_speed, 'N/A')}</span>
                            <span>🆔 {safeValue(adapter.mac_address, 'N/A')}</span>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </section>
    
    <!-- Algorithm Visualization -->
    <section class="card algorithm-section">
        <div class="card-header">
            <h2>📈 Algoritmos de Congestión</h2>
            <button 
                class="toggle-btn" 
                on:click={() => showAlgorithmCharts = !showAlgorithmCharts}
                title={showAlgorithmCharts ? 'Ocultar gráficas' : 'Mostrar gráficas'}
            >
                {showAlgorithmCharts ? 'Ocultar' : 'Ver comparativa'}
                <Icon name={showAlgorithmCharts ? 'chevron-up' : 'chevron-down'} size={14} />
            </button>
        </div>
        
        <p class="algorithm-intro">
            Windows usa <strong>CUBIC</strong> como algoritmo base. NetBoozt aplica técnicas similares a <strong>BBR</strong> 
            (HyStart++, PRR, Pacing, ECN) para mejorar el comportamiento.
        </p>
        
        {#if showAlgorithmCharts}
            <div class="algorithm-charts">
                <div class="algorithm-chart-wrapper">
                    <h4>CUBIC (Tradicional)</h4>
                    <p class="chart-desc">Reduce velocidad 50% ante pérdidas</p>
                    <AlgorithmChart algorithm="cubic" animated compact />
                </div>
                <div class="algorithm-chart-wrapper">
                    <h4>BBR-like (Con optimizaciones)</h4>
                    <p class="chart-desc">Mantiene velocidad estable</p>
                    <AlgorithmChart algorithm="bbr-like" animated compact />
                </div>
            </div>
            <div class="algorithm-legend">
                <span class="legend-item"><span class="dot loss"></span> Pérdida de paquete</span>
                <span class="legend-item"><span class="dot speed"></span> Velocidad de transmisión</span>
            </div>
        {/if}
    </section>
    
    <!-- Diagnostic -->
    <section class="card">
        <h2>🔍 Diagnóstico de Red</h2>
        <button class="btn btn-primary btn-lg" on:click={() => dispatch('diagnose')} disabled={diagnosing}>
            {#if diagnosing}
                <span class="spinner-small"></span> Diagnosticando...
            {:else}
                Ejecutar Diagnóstico de 4 Fases
            {/if}
        </button>
        <DiagnosticChain {diagnostic} loading={diagnosing} />
        
        <!-- Historial de diagnósticos -->
        <div class="diagnostic-history-section">
            <DiagnosticHistory 
                compact 
                limit={5}
                on:viewDetails={handleViewDiagnosticDetails}
                on:viewAll={handleViewAllDiagnostics}
            />
        </div>
    </section>
</div>

<style>
    .dashboard { display: flex; flex-direction: column; gap: 1.5rem; }
    
    /* Metrics Section - Tráfico en vivo + Speed Test */
    .metrics-section {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    @media (max-width: 900px) {
        .metrics-section {
            grid-template-columns: 1fr;
        }
    }
    
    .live-traffic {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: var(--primary, #00d4aa);
    }
    
    .pulse-dot {
        width: 8px;
        height: 8px;
        background: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: pulse-animation 1.5s infinite;
    }
    
    @keyframes pulse-animation {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    .traffic-hint {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin: 0;
        padding: 0.5rem;
        background: rgba(0, 212, 170, 0.05);
        border-radius: 6px;
        border-left: 3px solid var(--primary, #00d4aa);
    }
    
    .speedtest-section {
        padding: 0 !important;
        background: transparent !important;
    }
    
    .speedtest-section :global(.speedtest-card) {
        height: 100%;
    }
    
    /* Quick Optimization Section */
    .quick-optimization {
        margin-bottom: 0.5rem;
    }
    
    .quick-optimization :global(.optimization-profiles) {
        border: 1px solid var(--border, #3d3d3d);
    }
    
    /* DNS Section */
    .dns-section {
        flex: 1;
        min-width: 340px;
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
    }
    
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; }
    .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1rem; }
    .card { background: var(--bg-card, #1a1a1a); border-radius: 12px; padding: 1.25rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-primary, #fff); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .card-header h2 { margin: 0; }
    .header-actions { display: flex; gap: 0.5rem; align-items: center; }
    
    /* Protocol Card */
    .protocol-card, .dns-card { min-height: 200px; }
    
    /* Web mode notice */
    .web-mode-notice {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.65rem 0.85rem;
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 8px;
        font-size: 0.75rem;
        color: var(--warning, #fdcb6e);
        margin-bottom: 1rem;
    }
    
    .doc-link-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.4rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-secondary, #a0a0a0);
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .doc-link-btn:hover {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .btn-accent {
        background: var(--primary, #00d4aa) !important;
        color: #000 !important;
        font-weight: 600;
    }
    
    .btn-accent:hover {
        background: #00e6b8 !important;
    }
    
    .loading-mini, .empty-mini {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 1.5rem;
        color: var(--text-muted, #666);
        font-size: 0.8125rem;
    }
    
    .spinner-mini {
        width: 20px;
        height: 20px;
        border: 2px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .error-mini {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 1.5rem;
        color: var(--error, #ff6b6b);
        font-size: 0.8125rem;
        text-align: center;
        background: rgba(255, 107, 107, 0.05);
        border-radius: 8px;
    }
    
    .error-mini.compact {
        flex-direction: row;
        padding: 1rem;
    }
    
    .protocol-header {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .detected-profile {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.85rem;
        background: rgba(255,255,255,0.05);
        border: 2px solid var(--profile-color);
        border-radius: 20px;
    }
    
    .profile-icon { font-size: 1rem; }
    .profile-name { font-size: 0.875rem; font-weight: 600; color: var(--profile-color); }
    .profile-action { font-size: 0.75rem; color: var(--text-secondary, #a0a0a0); }
    
    /* Settings Sections */
    .settings-section { margin-bottom: 1rem; }
    .settings-section.advanced {
        padding-top: 0.75rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary, #a0a0a0);
        margin: 0 0 0.5rem 0;
    }
    
    .section-hint {
        cursor: help;
        opacity: 0.6;
    }
    
    .section-note {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin: 0 0 0.65rem 0;
        line-height: 1.4;
    }
    
    .tcp-settings-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 0.65rem;
    }
    
    .tcp-settings-grid.compact {
        grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
        gap: 0.5rem;
    }
    
    .tcp-setting {
        position: relative;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        padding: 0.6rem;
        border-left: 3px solid var(--border, #3d3d3d);
        transition: all 0.15s;
        cursor: default;
    }
    
    .tcp-setting:hover {
        background: var(--bg-hover, #333);
    }
    
    .tcp-setting.enabled {
        border-left-color: var(--primary, #00d4aa);
    }
    
    .tcp-setting.mini {
        padding: 0.45rem;
    }
    
    .setting-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.25rem;
    }
    
    .setting-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-secondary, #a0a0a0);
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .info-btn {
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        padding: 0.15rem;
        cursor: pointer;
        opacity: 0;
        transition: all 0.15s;
        border-radius: 50%;
    }
    
    .tcp-setting:hover .info-btn { opacity: 1; }
    .info-btn:hover { color: var(--primary, #00d4aa); background: rgba(0,212,170,0.1); }
    
    .setting-value {
        display: block;
        font-size: 0.8125rem;
        font-weight: 500;
        color: var(--text-muted, #666);
        margin-bottom: 0.2rem;
    }
    
    .setting-value.mini {
        font-size: 0.75rem;
        margin-bottom: 0;
    }
    
    .setting-value.enabled {
        color: var(--primary, #00d4aa);
    }
    
    .setting-short-desc {
        display: block;
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        line-height: 1.3;
    }
    
    /* Tooltips */
    .tooltip {
        position: absolute;
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
        z-index: 100;
        min-width: 220px;
        max-width: 280px;
        padding: 0.75rem;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-size: 0.75rem;
        color: var(--text-primary, #fff);
        pointer-events: none;
    }
    
    .tooltip.compact {
        min-width: 180px;
        padding: 0.6rem;
    }
    
    .tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: var(--border, #3d3d3d);
    }
    
    .tooltip strong {
        display: block;
        color: var(--primary, #00d4aa);
        margin-bottom: 0.35rem;
    }
    
    .tooltip p {
        margin: 0 0 0.5rem 0;
        line-height: 1.4;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .tooltip-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        font-size: 0.65rem;
        border-top: 1px solid var(--border, #3d3d3d);
        padding-top: 0.5rem;
        margin-top: 0.35rem;
    }
    
    .impact {
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
    }
    
    .impact-high { background: rgba(244,67,54,0.15); color: #F44336; }
    .impact-medium { background: rgba(255,193,7,0.15); color: #FFC107; }
    .impact-low { background: rgba(76,175,80,0.15); color: #4CAF50; }
    
    .profiles {
        color: var(--text-muted, #666);
    }
    
    /* DNS Card */
    .dns-mode {
        margin-bottom: 1rem;
    }
    
    .dhcp-badge, .static-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 6px;
    }
    
    .dhcp-badge {
        background: rgba(255, 193, 7, 0.15);
        color: var(--warning, #fdcb6e);
    }
    
    .static-badge {
        background: rgba(0, 212, 170, 0.15);
        color: var(--primary, #00d4aa);
    }
    
    .dns-hint {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
        margin: 0.5rem 0 0 0;
    }
    
    .dns-hint.good {
        color: var(--primary, #00d4aa);
    }
    
    .failover-explanation {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(0, 212, 170, 0.08);
        border-radius: 6px;
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
        margin-bottom: 0.75rem;
    }
    
    .dns-servers-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .dns-server-item {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        padding: 0.65rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        border-left: 3px solid var(--border, #3d3d3d);
    }
    
    .dns-server-item.primary {
        border-left-color: var(--primary, #00d4aa);
    }
    
    .dns-server-item.fallback {
        opacity: 0.75;
        padding: 0.5rem 0.65rem;
    }
    
    .dns-rank {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--text-muted, #666);
        letter-spacing: 0.5px;
    }
    
    .dns-server-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .dns-icon { font-size: 1rem; }
    
    .dns-ip {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
    }
    
    .dns-provider {
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .tier-badge {
        font-size: 0.625rem;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
    }
    
    .tier-badge.tier-1 { background: rgba(0, 212, 170, 0.2); color: var(--primary, #00d4aa); }
    .tier-badge.tier-2 { background: rgba(66, 133, 244, 0.2); color: #4285F4; }
    .tier-badge.tier-3 { background: rgba(156, 39, 176, 0.2); color: #9C27B0; }
    
    .dns-warning {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.65rem;
        background: rgba(255, 193, 7, 0.1);
        border-radius: 8px;
        font-size: 0.75rem;
        color: var(--warning, #fdcb6e);
    }
    
    /* Adapters */
    .adapter-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
    .adapter-card { background: var(--bg-elevated, #2b2b2b); border-radius: 10px; padding: 1rem; border: 2px solid transparent; transition: all 0.2s; }
    .adapter-card.selected { border-color: var(--primary, #00d4aa); }
    .adapter-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .adapter-card h3 { font-size: 0.9375rem; font-weight: 600; color: var(--primary, #00d4aa); margin: 0; }
    .status-badge { font-size: 0.625rem; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
    .status-badge.up { background: rgba(0, 212, 170, 0.2); color: var(--primary, #00d4aa); }
    .adapter-desc { font-size: 0.75rem; color: var(--text-muted, #666); margin: 0 0 0.75rem 0; }
    .adapter-stats { display: flex; gap: 1rem; font-size: 0.7rem; color: var(--text-secondary, #a0a0a0); }
    
    /* Buttons & misc */
    .empty-state { text-align: center; padding: 2rem; color: var(--text-muted, #666); }
    .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; transition: all 0.15s; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-primary { background: var(--primary, #00d4aa); color: #000; }
    .btn-primary:hover:not(:disabled) { background: #00e6b8; }
    .btn-lg { padding: 0.875rem 1.5rem; font-size: 0.9375rem; }
    .btn-sm { padding: 0.4rem 0.75rem; font-size: 0.75rem; margin-top: 0.5rem; background: var(--bg-elevated, #2b2b2b); color: var(--text-secondary, #a0a0a0); }
    .btn-sm:hover { background: var(--primary, #00d4aa); color: #000; }
    .spinner-small { width: 16px; height: 16px; border: 2px solid rgba(0,0,0,0.2); border-top-color: #000; border-radius: 50%; animation: spin 1s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    
    /* Algorithm Section */
    .algorithm-section {
        background: var(--bg-card, #1a1a1a);
    }
    
    .toggle-btn {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.4rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .toggle-btn:hover {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .algorithm-intro {
        font-size: 0.8125rem;
        color: var(--text-secondary, #a0a0a0);
        margin: 0;
        line-height: 1.5;
    }
    
    .algorithm-intro strong {
        color: var(--primary, #00d4aa);
    }
    
    .algorithm-charts {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .algorithm-chart-wrapper {
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
        padding: 1rem;
    }
    
    .algorithm-chart-wrapper h4 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0 0 0.25rem 0;
    }
    
    .chart-desc {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin: 0 0 0.75rem 0;
    }
    
    .algorithm-legend {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    
    .dot.loss {
        background: var(--error, #ff6b6b);
    }
    
    .dot.speed {
        background: var(--primary, #00d4aa);
    }
    
    /* Diagnostic History Section */
    .diagnostic-history-section {
        margin-top: 1.25rem;
        padding-top: 1.25rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
</style>
