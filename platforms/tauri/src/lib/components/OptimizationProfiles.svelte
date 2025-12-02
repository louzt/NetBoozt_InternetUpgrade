<!--
    OptimizationProfiles.svelte - Componente de perfiles de optimización TCP/IP
    Modular: puede usarse en Dashboard o en su propia tab
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import ProfileCard from './ProfileCard.svelte';
    import SkeletonCard from './SkeletonCard.svelte';
    import Icon from './Icon.svelte';
    
    // Props
    export let loading = false;
    export let optimizing = false;
    export let tcpSettings: any = null;
    export let dryRunMode = false;
    export let compact = false; // Para Dashboard: vista compacta
    export let showSettings = true; // Mostrar configuración actual
    export let showReset = true; // Mostrar botón de reset
    
    const dispatch = createEventDispatcher();
    
    // Detectar perfil actual basado en settings
    $: currentProfile = detectCurrentProfile(tcpSettings);
    $: profileScore = calculateProfileScore(tcpSettings);
    
    /**
     * Detecta el perfil actual basado en la configuración TCP
     * Considera TODAS las optimizaciones, no solo algunas
     */
    function detectCurrentProfile(settings: any): 'none' | 'conservative' | 'balanced' | 'aggressive' {
        if (!settings) return 'none';
        
        const score = calculateProfileScore(settings);
        
        // Umbrales basados en puntuación total
        if (score.total >= 80) return 'aggressive';
        if (score.total >= 50) return 'balanced';
        if (score.total >= 25) return 'conservative';
        
        return 'none';
    }
    
    /**
     * Calcula una puntuación detallada de las optimizaciones activas
     */
    function calculateProfileScore(settings: any): { 
        total: number; 
        basic: number; 
        balanced: number; 
        aggressive: number;
        details: Record<string, boolean>;
    } {
        if (!settings) return { total: 0, basic: 0, balanced: 0, aggressive: 0, details: {} };
        
        const isEnabled = (val: string | undefined): boolean => {
            if (!val) return false;
            const v = val.toLowerCase();
            return v.includes('enabled') || v === 'normal' || v === 'experimental' || 
                   v === 'always' || v.includes('habilitado');
        };
        
        const isAutotuningOptimized = (val: string | undefined): boolean => {
            if (!val) return false;
            const v = val.toLowerCase();
            return v === 'normal' || v === 'experimental' || v === 'highlyrestricted' || v === 'restricted';
        };
        
        const isRtoReduced = (val: string | undefined): boolean => {
            if (!val) return false;
            // Parsear valor como número (ej: "1000ms" o "1000")
            const match = val.match(/(\d+)/);
            if (match) {
                const ms = parseInt(match[1], 10);
                return ms < 3000; // Default es 3000ms
            }
            return false;
        };
        
        // Detectar cada optimización
        const details: Record<string, boolean> = {
            // Básicas (10 pts cada una = 30 pts max)
            rss: isEnabled(settings.rss),
            rsc: isEnabled(settings.rsc),
            autotuning: isAutotuningOptimized(settings.autotuning),
            
            // Balanceadas (10 pts cada una = 30 pts max)
            ecn: isEnabled(settings.ecn),
            hystart: isEnabled(settings.hystart),
            prr: isEnabled(settings.prr),
            
            // Agresivas (10 pts cada una = 40 pts max)
            timestamps: isEnabled(settings.timestamps),
            fast_open: isEnabled(settings.fast_open),
            pacing: settings.pacing?.toLowerCase() === 'always',
            initial_rto: isRtoReduced(settings.initial_rto),
        };
        
        // Calcular puntuaciones por categoría
        const basic = (details.rss ? 10 : 0) + (details.rsc ? 10 : 0) + (details.autotuning ? 10 : 0);
        const balanced = (details.ecn ? 10 : 0) + (details.hystart ? 10 : 0) + (details.prr ? 10 : 0);
        const aggressive = (details.timestamps ? 10 : 0) + (details.fast_open ? 10 : 0) + 
                          (details.pacing ? 10 : 0) + (details.initial_rto ? 10 : 0);
        
        return {
            total: basic + balanced + aggressive,
            basic,
            balanced,
            aggressive,
            details
        };
    }
    
    function getSettingStatus(value: string | undefined): 'enabled' | 'disabled' | 'unknown' {
        if (!value) return 'unknown';
        const v = value.toLowerCase();
        if (v.includes('enabled') || v === 'normal' || v.includes('habilitado')) return 'enabled';
        if (v.includes('disabled') || v.includes('deshabilitado')) return 'disabled';
        return 'unknown';
    }
    
    function applyProfile(profile: string) {
        dispatch('applyProfile', profile);
    }
    
    function toggleDryRun() {
        dispatch('toggleDryRun');
    }
    
    function resetSettings() {
        dispatch('reset');
    }
</script>

<div class="optimization-profiles" class:compact>
    <div class="profiles-header">
        <div class="header-left">
            <h3>⚡ Perfiles de Optimización</h3>
            {#if currentProfile !== 'none'}
                <span class="current-profile-badge" class:conservative={currentProfile === 'conservative'}
                      class:balanced={currentProfile === 'balanced'} class:aggressive={currentProfile === 'aggressive'}>
                    {#if currentProfile === 'conservative'}🟢 Conservador
                    {:else if currentProfile === 'balanced'}🟡 Balanceado
                    {:else if currentProfile === 'aggressive'}🔴 Agresivo
                    {/if}
                    <span class="score-badge">{profileScore.total}%</span>
                </span>
            {:else}
                <span class="current-profile-badge none">⚪ Sin optimizar</span>
            {/if}
        </div>
        <div class="header-right">
            <label class="dryrun-toggle">
                <input type="checkbox" checked={dryRunMode} on:change={toggleDryRun} />
                <span class="toggle-slider"></span>
                <span class="toggle-label">🧪 Dry-Run</span>
            </label>
        </div>
    </div>
    
    {#if dryRunMode}
        <p class="dryrun-notice">⚠️ Modo simulación - Los comandos se mostrarán sin aplicarse</p>
    {:else if !compact}
        <p class="profiles-desc">Selecciona un perfil según tu necesidad. Todas las optimizaciones son reversibles.</p>
    {/if}
    
    <div class="profile-grid" class:compact>
        {#if loading}
            {#each [1,2,3] as _}
                <SkeletonCard variant="profile" />
            {/each}
        {:else}
            <ProfileCard 
                name="Conservador" icon="🟢" color="green"
                description={compact ? "Seguro" : "Optimizaciones seguras con mínimo riesgo."}
                features={compact ? ['RSS', 'RSC', 'Autotuning'] : ['RSS habilitado', 'RSC habilitado', 'Autotuning normal']}
                loading={optimizing}
                active={currentProfile === 'conservative'}
                {compact}
                onApply={() => applyProfile('Conservative')}
            />
            <ProfileCard 
                name="Balanceado" icon="🟡" color="yellow"
                description={compact ? "Recomendado" : "Mejor rendimiento con bajo riesgo. Recomendado."}
                features={compact ? ['+ECN', '+HyStart++', '+PRR'] : ['Todo lo anterior', 'ECN habilitado', 'HyStart++', 'PRR']}
                recommended={true} loading={optimizing}
                active={currentProfile === 'balanced'}
                {compact}
                onApply={() => applyProfile('Balanced')}
            />
            <ProfileCard 
                name="Agresivo" icon="🔴" color="red"
                description={compact ? "Avanzado" : "Máximo rendimiento. Para usuarios avanzados."}
                features={compact ? ['+TFO', '+Pacing', '+RTO'] : ['Todo lo anterior', 'TCP Fast Open', 'TCP Pacing', 'Initial RTO reducido']}
                loading={optimizing}
                active={currentProfile === 'aggressive'}
                {compact}
                onApply={() => applyProfile('Aggressive')}
            />
        {/if}
    </div>
    
    {#if showReset && !compact}
        <div class="reset-section">
            <button class="btn btn-danger" on:click={resetSettings} disabled={optimizing}>
                🔄 Restaurar valores por defecto
            </button>
        </div>
    {/if}
    
    {#if showSettings && tcpSettings && !compact}
        <div class="current-settings">
            <h4>📋 Configuración TCP Actual</h4>
            <div class="settings-grid">
                <div class="setting-item" class:enabled={getSettingStatus(tcpSettings.autotuning) === 'enabled'}>
                    <span class="setting-label">Autotuning</span>
                    <span class="setting-value">{tcpSettings.autotuning || 'N/A'}</span>
                </div>
                <div class="setting-item" class:enabled={getSettingStatus(tcpSettings.rss) === 'enabled'}>
                    <span class="setting-label">RSS</span>
                    <span class="setting-value">{tcpSettings.rss || 'N/A'}</span>
                </div>
                <div class="setting-item" class:enabled={getSettingStatus(tcpSettings.rsc) === 'enabled'}>
                    <span class="setting-label">RSC</span>
                    <span class="setting-value">{tcpSettings.rsc || 'N/A'}</span>
                </div>
                <div class="setting-item" class:enabled={getSettingStatus(tcpSettings.ecn) === 'enabled'}>
                    <span class="setting-label">ECN</span>
                    <span class="setting-value">{tcpSettings.ecn || 'N/A'}</span>
                </div>
                <div class="setting-item" class:enabled={getSettingStatus(tcpSettings.timestamps) === 'enabled'}>
                    <span class="setting-label">Timestamps</span>
                    <span class="setting-value">{tcpSettings.timestamps || 'N/A'}</span>
                </div>
                {#if tcpSettings.congestion_provider}
                    <div class="setting-item highlight">
                        <span class="setting-label">Congestion</span>
                        <span class="setting-value">{tcpSettings.congestion_provider}</span>
                    </div>
                {/if}
            </div>
        </div>
    {/if}
</div>

<style>
    .optimization-profiles {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 1.25rem;
    }
    
    .optimization-profiles.compact {
        padding: 1rem;
    }
    
    .profiles-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .profiles-header h3 {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0;
    }
    
    .compact .profiles-header h3 {
        font-size: 0.9375rem;
    }
    
    .current-profile-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.6875rem;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-weight: 600;
    }
    
    .current-profile-badge.none {
        background: rgba(158, 158, 158, 0.15);
        color: #9e9e9e;
        border: 1px solid rgba(158, 158, 158, 0.3);
    }
    
    .score-badge {
        background: rgba(0, 0, 0, 0.2);
        padding: 0.1rem 0.35rem;
        border-radius: 8px;
        font-size: 0.6rem;
        font-weight: 700;
    }
    
    .current-profile-badge.conservative {
        background: rgba(46, 204, 113, 0.15);
        color: #2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.3);
    }
    
    .current-profile-badge.balanced {
        background: rgba(241, 196, 15, 0.15);
        color: #f1c40f;
        border: 1px solid rgba(241, 196, 15, 0.3);
    }
    
    .current-profile-badge.aggressive {
        background: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    
    .dryrun-toggle {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
    }
    
    .dryrun-toggle input {
        display: none;
    }
    
    .toggle-slider {
        width: 36px;
        height: 20px;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
        position: relative;
        transition: background 0.2s;
    }
    
    .toggle-slider::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        background: var(--text-muted, #666);
        border-radius: 50%;
        top: 2px;
        left: 2px;
        transition: transform 0.2s, background 0.2s;
    }
    
    .dryrun-toggle input:checked + .toggle-slider {
        background: var(--warning, #fdcb6e);
    }
    
    .dryrun-toggle input:checked + .toggle-slider::after {
        transform: translateX(16px);
        background: #fff;
    }
    
    .toggle-label {
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .dryrun-notice {
        font-size: 0.75rem;
        color: var(--warning, #fdcb6e);
        background: rgba(253, 203, 110, 0.1);
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(253, 203, 110, 0.2);
    }
    
    .profiles-desc {
        font-size: 0.8125rem;
        color: var(--text-muted, #666);
        margin: 0 0 1rem 0;
    }
    
    .profile-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
    
    .profile-grid.compact {
        gap: 0.75rem;
    }
    
    @media (max-width: 900px) {
        .profile-grid {
            grid-template-columns: 1fr;
        }
    }
    
    .reset-section {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border, #3d3d3d);
        text-align: center;
    }
    
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
    
    .btn-danger {
        background: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.3);
    }
    
    .btn-danger:hover:not(:disabled) {
        background: #e74c3c;
        color: #fff;
    }
    
    /* Settings Grid */
    .current-settings {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .current-settings h4 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary, #a0a0a0);
        margin: 0 0 0.75rem 0;
    }
    
    .settings-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 0.5rem;
    }
    
    .setting-item {
        display: flex;
        flex-direction: column;
        padding: 0.5rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 6px;
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .setting-item.enabled {
        border-color: rgba(0, 212, 170, 0.3);
        background: rgba(0, 212, 170, 0.05);
    }
    
    .setting-item.highlight {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.1);
    }
    
    .setting-label {
        font-size: 0.625rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .setting-value {
        font-size: 0.8125rem;
        font-weight: 500;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .setting-item.enabled .setting-value {
        color: var(--primary, #00d4aa);
    }
</style>
