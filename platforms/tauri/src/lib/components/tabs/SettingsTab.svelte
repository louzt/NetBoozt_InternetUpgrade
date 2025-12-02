<!--
    SettingsTab.svelte - Tab de Configuración
    By LOUST
-->
<script lang="ts">
    export let settings = {
        minimizeToTray: true,
        startWithWindows: false,
        showNotifications: true,
        soundOnAlerts: true,
        updateInterval: 1000
    };
</script>

<div class="settings-page">
    <section class="card">
        <h2>⚙️ Configuración</h2>
        
        <div class="setting-group">
            <h3>Comportamiento</h3>
            <label class="toggle-setting">
                <input type="checkbox" bind:checked={settings.minimizeToTray} />
                <span>Minimizar a bandeja al cerrar</span>
            </label>
            <label class="toggle-setting">
                <input type="checkbox" bind:checked={settings.startWithWindows} />
                <span>Iniciar con Windows</span>
            </label>
            <label class="toggle-setting">
                <input type="checkbox" bind:checked={settings.showNotifications} />
                <span>Mostrar notificaciones</span>
            </label>
            <label class="toggle-setting">
                <input type="checkbox" bind:checked={settings.soundOnAlerts} />
                <span>Sonido en alertas</span>
            </label>
        </div>
        
        <div class="setting-group">
            <h3>Monitoreo</h3>
            <div class="setting-row">
                <span>Intervalo de actualización</span>
                <select bind:value={settings.updateInterval}>
                    <option value={500}>0.5 segundos</option>
                    <option value={1000}>1 segundo</option>
                    <option value={2000}>2 segundos</option>
                </select>
            </div>
        </div>
        
        <div class="setting-group">
            <h3>Acerca de</h3>
            <p><strong>NetBoozt</strong> v3.0.0</p>
            <p>Network Optimization Tool for Windows</p>
            <p>Desarrollado con Rust + Tauri + Svelte</p>
            <p class="text-muted">By <a href="https://loust.pro" target="_blank">LOUST</a> | <a href="https://github.com/louzt/NetBoozt_InternetUpgrade" target="_blank">GitHub</a></p>
        </div>
    </section>
</div>

<style>
    .settings-page { display: flex; flex-direction: column; gap: 1.5rem; }
    .card { background: var(--bg-card, #1a1a1a); border-radius: 12px; padding: 1.25rem; }
    .card h2 { font-size: 1rem; font-weight: 600; margin: 0 0 1rem 0; color: var(--text-primary, #fff); }
    .setting-group { margin-bottom: 1.5rem; }
    .setting-group h3 { font-size: 0.875rem; font-weight: 600; color: var(--text-secondary, #a0a0a0); margin: 0 0 0.75rem 0; }
    .toggle-setting { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; background: var(--bg-elevated, #2b2b2b); border-radius: 8px; margin-bottom: 0.5rem; cursor: pointer; font-size: 0.875rem; color: var(--text-primary, #fff); }
    .toggle-setting input { width: 18px; height: 18px; accent-color: var(--primary, #00d4aa); }
    .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: var(--bg-elevated, #2b2b2b); border-radius: 8px; font-size: 0.875rem; color: var(--text-primary, #fff); }
    .setting-row select { background: var(--bg-card, #1a1a1a); color: var(--text-primary, #fff); border: 1px solid var(--border, #3d3d3d); border-radius: 6px; padding: 0.375rem 0.75rem; font-size: 0.8125rem; }
    .text-muted { color: var(--text-muted, #666); }
    .text-muted a { color: var(--primary, #00d4aa); text-decoration: none; }
</style>
