<!--
    OptimizeTab.svelte - Tab de Optimizaciones TCP/IP
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import ProfileCard from '../ProfileCard.svelte';
    import SkeletonCard from '../SkeletonCard.svelte';
    import Icon from '../Icon.svelte';
    
    export let loading = false;
    export let optimizing = false;
    export let tcpSettings: any = null;
    export let dryRunMode = false;
    
    const dispatch = createEventDispatcher();
    
    // Comandos por perfil para mostrar en dry-run
    const profileCommands: Record<string, string[]> = {
        'Conservative': [
            'netsh int tcp set global rss=enabled',
            'netsh int tcp set global rsc=enabled',
            'netsh int tcp set global autotuninglevel=normal',
        ],
        'Balanced': [
            'netsh int tcp set global rss=enabled',
            'netsh int tcp set global rsc=enabled',
            'netsh int tcp set global autotuninglevel=normal',
            'netsh int tcp set global ecncapability=enabled',
            'reg add "HKLM\\...\\Tcpip\\Parameters" /v EnableHyStart /d 1',
            'reg add "HKLM\\...\\Tcpip\\Parameters" /v EnablePrr /d 1',
        ],
        'Aggressive': [
            '...todo lo de Balanceado +',
            'netsh int tcp set global timestamps=enabled',
            'reg add "...\\Tcpip\\Parameters" /v EnableTFO /d 1',
            'reg add "...\\Tcpip\\Parameters" /v EnableWsd /d 0',
            'reg add "...\\Tcpip\\Parameters" /v TcpInitialRto /d 1000',
        ],
    };
    
    function getSettingStatus(value: string | undefined): 'enabled' | 'disabled' | 'unknown' {
        if (!value) return 'unknown';
        const v = value.toLowerCase();
        if (v.includes('enabled') || v === 'normal') return 'enabled';
        if (v.includes('disabled')) return 'disabled';
        return 'unknown';
    }
</script>

<div class="optimize-page">
    <section class="card">
        <div class="card-header">
            <h2>⚡ Perfiles de Optimización</h2>
            <div class="dryrun-toggle">
                <label class="toggle">
                    <input type="checkbox" checked={dryRunMode} on:change={() => dispatch('toggleDryRun')} />
                    <span class="toggle-slider"></span>
                </label>
                <span class="dryrun-label">🧪 Dry-Run</span>
            </div>
        </div>
        <p class="card-desc">
            {#if dryRunMode}
                <span class="dryrun-notice">⚠️ Modo simulación activo - No se aplicarán cambios reales</span>
            {:else}
                Selecciona un perfil según tu necesidad. Todas las optimizaciones son reversibles.
            {/if}
        </p>
        
        <div class="profile-grid">
            {#if loading}
                {#each [1,2,3] as _}
                    <SkeletonCard variant="profile" />
                {/each}
            {:else}
                <ProfileCard 
                    name="Conservador" icon="🟢" color="green"
                    description="Optimizaciones seguras con mínimo riesgo."
                    features={['RSS habilitado', 'RSC habilitado', 'Autotuning normal']}
                    loading={optimizing}
                    onApply={() => dispatch('applyProfile', 'Conservative')}
                />
                <ProfileCard 
                    name="Balanceado" icon="🟡" color="yellow"
                    description="Mejor rendimiento con bajo riesgo. Recomendado."
                    features={['Todo lo anterior', 'ECN habilitado', 'HyStart++', 'PRR']}
                    recommended={true} loading={optimizing}
                    onApply={() => dispatch('applyProfile', 'Balanced')}
                />
                <ProfileCard 
                    name="Agresivo" icon="🔴" color="red"
                    description="Máximo rendimiento. Para usuarios avanzados."
                    features={['Todo lo anterior', 'TCP Fast Open', 'TCP Pacing', 'Initial RTO reducido']}
                    loading={optimizing}
                    onApply={() => dispatch('applyProfile', 'Aggressive')}
                />
            {/if}
        </div>
        
        <div class="reset-section">
            <button class="btn btn-danger" on:click={() => dispatch('reset')} disabled={optimizing}>
                🔄 Restaurar valores por defecto
            </button>
        </div>
    </section>
    
    {#if tcpSettings}
        <section class="card">
            <h2>📋 Configuración TCP Actual</h2>
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
                <div class="setting-item">
                    <span class="setting-label">Chimney</span>
                    <span class="setting-value">{tcpSettings.chimney || 'N/A'}</span>
                </div>
                {#if tcpSettings.congestion_provider}
                    <div class="setting-item full-width">
                        <span class="setting-label">Congestion Provider</span>
                        <span class="setting-value highlight">{tcpSettings.congestion_provider}</span>
                    </div>
                {/if}
            </div>
        </section>
    {/if}
    
    {#if dryRunMode}
        <section class="card dryrun-info-card">
            <h2>🧪 Modo Dry-Run Activo</h2>
            <p class="dryrun-explanation">
                En este modo, al hacer clic en un perfil se mostrarán los comandos que se ejecutarían 
                <strong>sin aplicar cambios reales</strong>. Los comandos aparecerán en la terminal inferior.
            </p>
            <div class="dryrun-preview">
                <h4>Ejemplo de comandos (Perfil Balanceado):</h4>
                <div class="command-list">
                    {#each profileCommands['Balanced'] as cmd}
                        <code class="command-line">{cmd}</code>
                    {/each}
                </div>
            </div>
        </section>
    {/if}
</div>

<style>
    .optimize-page { display: flex; flex-direction: column; gap: 1.5rem; }
    .card { background: var(--bg-card, #1a1a1a); border-radius: 12px; padding: 1.25rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-primary, #fff); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
    .card-header h2 { margin-bottom: 0; }
    .card-desc { font-size: 0.875rem; color: var(--text-secondary, #a0a0a0); margin-bottom: 1rem; }
    .profile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem; }
    .settings-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.75rem; }
    .setting-item { display: flex; justify-content: space-between; align-items: center; padding: 0.625rem 0.875rem; background: var(--bg-elevated, #2b2b2b); border-radius: 8px; border-left: 3px solid var(--border, #3d3d3d); transition: border-color 0.2s; }
    .setting-item.enabled { border-left-color: var(--primary, #00d4aa); }
    .setting-item.full-width { grid-column: 1 / -1; }
    .setting-label { font-size: 0.8125rem; color: var(--text-secondary, #a0a0a0); }
    .setting-value { font-size: 0.8125rem; font-weight: 500; color: var(--text-primary, #fff); }
    .setting-value.highlight { color: var(--primary, #00d4aa); }
    
    .dryrun-info-card { border: 2px dashed var(--warning, #fdcb6e); background: rgba(253, 203, 110, 0.05); }
    .dryrun-info-card h2 { color: var(--warning, #fdcb6e); }
    .dryrun-explanation { font-size: 0.875rem; color: var(--text-secondary, #a0a0a0); margin-bottom: 1rem; line-height: 1.5; }
    .dryrun-preview { background: var(--bg-elevated, #2b2b2b); border-radius: 8px; padding: 1rem; }
    .dryrun-preview h4 { font-size: 0.75rem; color: var(--text-muted, #666); margin: 0 0 0.75rem 0; text-transform: uppercase; }
    .command-list { display: flex; flex-direction: column; gap: 0.35rem; }
    .command-line { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--warning, #fdcb6e); background: rgba(0,0,0,0.3); padding: 0.35rem 0.5rem; border-radius: 4px; overflow-x: auto; white-space: nowrap; }
    
    .reset-section { border-top: 1px solid var(--border, #2d2d2d); padding-top: 1.25rem; margin-top: 0.5rem; }
    .dryrun-toggle { display: flex; align-items: center; gap: 0.5rem; }
    .dryrun-label { font-size: 0.8125rem; color: var(--warning, #fdcb6e); }
    .dryrun-notice { color: var(--warning, #fdcb6e); font-weight: 500; }
    .toggle { position: relative; width: 44px; height: 24px; }
    .toggle input { opacity: 0; width: 0; height: 0; }
    .toggle-slider { position: absolute; cursor: pointer; inset: 0; background: var(--bg-elevated, #2b2b2b); border-radius: 24px; transition: 0.3s; }
    .toggle-slider::before { content: ''; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px; background: var(--text-muted, #666); border-radius: 50%; transition: 0.3s; }
    .toggle input:checked + .toggle-slider { background: rgba(253, 203, 110, 0.3); }
    .toggle input:checked + .toggle-slider::before { transform: translateX(20px); background: var(--warning, #fdcb6e); }
    .btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; cursor: pointer; border: none; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .btn-danger { background: var(--error, #ff6b6b); color: #fff; }
    .btn-danger:hover:not(:disabled) { background: #ff5252; }
</style>
