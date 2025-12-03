<!--
    SettingsTab.svelte - Tab de Configuración Completa
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import Icon from '../Icon.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Configuraciones exportables
    export let settings = {
        // Comportamiento general
        minimizeToTray: true,
        startWithWindows: false,
        showNotifications: true,
        soundOnAlerts: true,
        
        // Monitoreo
        updateInterval: 1000,
        autoStartMonitoring: true,
        monitorPackets: true,
        monitorErrors: true,
        
        // DNS
        dnsAutoFailover: true,
        dnsCheckInterval: 30000,
        preferredDnsProvider: 'cloudflare',
        
        // Optimizaciones
        autoApplyOptimizations: false,
        optimizationProfile: 'balanced',
        
        // Apariencia
        theme: 'dark',
        accentColor: '#00d4aa',
        compactMode: false,
        animationsEnabled: true,
        
        // Avanzado
        debugMode: false,
        logLevel: 'info',
        cacheEnabled: true,
        maxLogSize: 10
    };
    
    // Temas disponibles
    const THEMES = [
        { id: 'dark', name: 'Oscuro', icon: '🌙' },
        { id: 'light', name: 'Claro', icon: '☀️' },
        { id: 'system', name: 'Sistema', icon: '💻' },
        { id: 'midnight', name: 'Medianoche', icon: '🌌' },
        { id: 'forest', name: 'Bosque', icon: '🌲' }
    ];
    
    // Colores de acento
    const ACCENT_COLORS = [
        { color: '#00d4aa', name: 'Verde NetBoozt' },
        { color: '#3b82f6', name: 'Azul' },
        { color: '#8b5cf6', name: 'Púrpura' },
        { color: '#f59e0b', name: 'Naranja' },
        { color: '#ef4444', name: 'Rojo' },
        { color: '#ec4899', name: 'Rosa' },
        { color: '#06b6d4', name: 'Cyan' }
    ];
    
    // Perfiles de optimización
    const OPTIMIZATION_PROFILES = [
        { id: 'conservative', name: 'Conservador', desc: 'Cambios mínimos, máxima estabilidad', icon: '🛡️' },
        { id: 'balanced', name: 'Balanceado', desc: 'Balance entre rendimiento y estabilidad', icon: '⚖️' },
        { id: 'aggressive', name: 'Agresivo', desc: 'Máximo rendimiento, puede afectar estabilidad', icon: '🚀' }
    ];
    
    // DNS Providers
    const DNS_PROVIDERS = [
        { id: 'cloudflare', name: 'Cloudflare', ip: '1.1.1.1' },
        { id: 'google', name: 'Google', ip: '8.8.8.8' },
        { id: 'quad9', name: 'Quad9', ip: '9.9.9.9' },
        { id: 'opendns', name: 'OpenDNS', ip: '208.67.222.222' },
        { id: 'adguard', name: 'AdGuard', ip: '94.140.14.14' }
    ];
    
    const STORAGE_KEY = 'netboozt_settings';
    
    // Cargar settings de localStorage
    onMount(() => {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                settings = { ...settings, ...parsed };
            } catch (e) {
                console.warn('Error loading settings:', e);
            }
        }
        applyTheme(settings.theme);
        applyAccentColor(settings.accentColor);
    });
    
    // Guardar settings
    function saveSettings() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
        dispatch('settingsChanged', settings);
    }
    
    // Aplicar tema
    function applyTheme(theme: string) {
        document.documentElement.setAttribute('data-theme', theme);
        saveSettings();
    }
    
    // Aplicar color de acento
    function applyAccentColor(color: string) {
        document.documentElement.style.setProperty('--primary', color);
        document.documentElement.style.setProperty('--accent', color);
        saveSettings();
    }
    
    // Reset a valores por defecto
    function resetToDefaults() {
        if (confirm('¿Restaurar todas las configuraciones a los valores por defecto?')) {
            localStorage.removeItem(STORAGE_KEY);
            location.reload();
        }
    }
    
    // Exportar configuración
    function exportSettings() {
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'netboozt-settings.json';
        a.click();
        URL.revokeObjectURL(url);
    }
    
    // Importar configuración
    function importSettings(event: Event) {
        const input = event.target as HTMLInputElement;
        const file = input.files?.[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const imported = JSON.parse(e.target?.result as string);
                settings = { ...settings, ...imported };
                saveSettings();
                dispatch('toast', { type: 'success', message: 'Configuración importada correctamente' });
            } catch {
                dispatch('toast', { type: 'error', message: 'Error al importar configuración' });
            }
        };
        reader.readAsText(file);
    }
    
    // Reactive para guardar cambios
    $: if (settings) saveSettings();
</script>

<div class="settings-page">
    <!-- Header -->
    <header class="settings-header">
        <div class="header-info">
            <Icon name="settings" size={22} />
            <div>
                <h1>Configuración</h1>
                <p>Personaliza NetBoozt a tu gusto</p>
            </div>
        </div>
    </header>
    
    <div class="settings-grid">
        <!-- Apariencia -->
        <section class="settings-card">
            <div class="card-header">
                <Icon name="palette" size={18} />
                <h2>Apariencia</h2>
            </div>
            
            <div class="setting-group">
                <label class="setting-label">Tema</label>
                <div class="theme-selector">
                    {#each THEMES as theme}
                        <button 
                            class="theme-option" 
                            class:active={settings.theme === theme.id}
                            on:click={() => { settings.theme = theme.id; applyTheme(theme.id); }}
                        >
                            <span class="theme-icon">{theme.icon}</span>
                            <span class="theme-name">{theme.name}</span>
                        </button>
                    {/each}
                </div>
            </div>
            
            <div class="setting-group">
                <label class="setting-label">Color de acento</label>
                <div class="color-selector">
                    {#each ACCENT_COLORS as { color, name }}
                        <button 
                            class="color-option" 
                            class:active={settings.accentColor === color}
                            style="--color: {color}"
                            title={name}
                            on:click={() => { settings.accentColor = color; applyAccentColor(color); }}
                        >
                            {#if settings.accentColor === color}
                                <Icon name="check" size={12} color="#fff" />
                            {/if}
                        </button>
                    {/each}
                </div>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Modo compacto</span>
                    <span class="toggle-desc">Reduce el espaciado de la interfaz</span>
                </span>
                <input type="checkbox" bind:checked={settings.compactMode} />
            </label>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Animaciones</span>
                    <span class="toggle-desc">Transiciones y efectos visuales</span>
                </span>
                <input type="checkbox" bind:checked={settings.animationsEnabled} />
            </label>
        </section>
        
        <!-- Comportamiento -->
        <section class="settings-card">
            <div class="card-header">
                <Icon name="sliders" size={18} />
                <h2>Comportamiento</h2>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Minimizar a bandeja</span>
                    <span class="toggle-desc">Al cerrar, minimizar en vez de salir</span>
                </span>
                <input type="checkbox" bind:checked={settings.minimizeToTray} />
            </label>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Iniciar con Windows</span>
                    <span class="toggle-desc">Ejecutar automáticamente al iniciar</span>
                </span>
                <input type="checkbox" bind:checked={settings.startWithWindows} />
            </label>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Notificaciones</span>
                    <span class="toggle-desc">Mostrar alertas del sistema</span>
                </span>
                <input type="checkbox" bind:checked={settings.showNotifications} />
            </label>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Sonido en alertas</span>
                    <span class="toggle-desc">Reproducir sonido en eventos</span>
                </span>
                <input type="checkbox" bind:checked={settings.soundOnAlerts} />
            </label>
        </section>
        
        <!-- Monitoreo -->
        <section class="settings-card">
            <div class="card-header">
                <Icon name="activity" size={18} />
                <h2>Monitoreo</h2>
            </div>
            
            <div class="setting-group">
                <label class="setting-label" for="updateInterval">Intervalo de actualización</label>
                <select id="updateInterval" bind:value={settings.updateInterval} class="setting-select">
                    <option value={500}>0.5 segundos (Alto consumo)</option>
                    <option value={1000}>1 segundo (Recomendado)</option>
                    <option value={2000}>2 segundos</option>
                    <option value={5000}>5 segundos (Bajo consumo)</option>
                </select>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Auto-iniciar monitoreo</span>
                    <span class="toggle-desc">Comenzar a monitorear al abrir</span>
                </span>
                <input type="checkbox" bind:checked={settings.autoStartMonitoring} />
            </label>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Monitorear paquetes</span>
                    <span class="toggle-desc">Contar paquetes enviados/recibidos</span>
                </span>
                <input type="checkbox" bind:checked={settings.monitorPackets} />
            </label>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Monitorear errores</span>
                    <span class="toggle-desc">Detectar errores y drops</span>
                </span>
                <input type="checkbox" bind:checked={settings.monitorErrors} />
            </label>
        </section>
        
        <!-- DNS -->
        <section class="settings-card">
            <div class="card-header">
                <Icon name="globe" size={18} />
                <h2>DNS</h2>
            </div>
            
            <div class="setting-group">
                <label class="setting-label" for="dnsProvider">Proveedor DNS preferido</label>
                <select id="dnsProvider" bind:value={settings.preferredDnsProvider} class="setting-select">
                    {#each DNS_PROVIDERS as provider}
                        <option value={provider.id}>{provider.name} ({provider.ip})</option>
                    {/each}
                </select>
            </div>
            
            <div class="setting-group">
                <label class="setting-label" for="dnsInterval">Intervalo de verificación DNS</label>
                <select id="dnsInterval" bind:value={settings.dnsCheckInterval} class="setting-select">
                    <option value={15000}>15 segundos</option>
                    <option value={30000}>30 segundos</option>
                    <option value={60000}>1 minuto</option>
                    <option value={300000}>5 minutos</option>
                </select>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Auto-failover DNS</span>
                    <span class="toggle-desc">Cambiar DNS automáticamente si falla</span>
                </span>
                <input type="checkbox" bind:checked={settings.dnsAutoFailover} />
            </label>
        </section>
        
        <!-- Optimizaciones -->
        <section class="settings-card">
            <div class="card-header">
                <Icon name="zap" size={18} />
                <h2>Optimizaciones</h2>
            </div>
            
            <div class="setting-group">
                <label class="setting-label">Perfil de optimización</label>
                <div class="profile-selector">
                    {#each OPTIMIZATION_PROFILES as profile}
                        <button 
                            class="profile-option" 
                            class:active={settings.optimizationProfile === profile.id}
                            on:click={() => settings.optimizationProfile = profile.id}
                        >
                            <span class="profile-icon">{profile.icon}</span>
                            <div class="profile-info">
                                <span class="profile-name">{profile.name}</span>
                                <span class="profile-desc">{profile.desc}</span>
                            </div>
                        </button>
                    {/each}
                </div>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Auto-aplicar optimizaciones</span>
                    <span class="toggle-desc">Aplicar al iniciar (requiere admin)</span>
                </span>
                <input type="checkbox" bind:checked={settings.autoApplyOptimizations} />
            </label>
        </section>
        
        <!-- Avanzado -->
        <section class="settings-card">
            <div class="card-header">
                <Icon name="terminal" size={18} />
                <h2>Avanzado</h2>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Modo debug</span>
                    <span class="toggle-desc">Mostrar información de depuración</span>
                </span>
                <input type="checkbox" bind:checked={settings.debugMode} />
            </label>
            
            <div class="setting-group">
                <label class="setting-label" for="logLevel">Nivel de log</label>
                <select id="logLevel" bind:value={settings.logLevel} class="setting-select">
                    <option value="error">Solo errores</option>
                    <option value="warn">Warnings y errores</option>
                    <option value="info">Info (Recomendado)</option>
                    <option value="debug">Debug (Verbose)</option>
                </select>
            </div>
            
            <label class="toggle-setting">
                <span class="toggle-info">
                    <span class="toggle-label">Caché habilitado</span>
                    <span class="toggle-desc">Almacenar datos temporalmente</span>
                </span>
                <input type="checkbox" bind:checked={settings.cacheEnabled} />
            </label>
        </section>
    </div>
    
    <!-- Actions -->
    <section class="settings-actions">
        <div class="action-group">
            <button class="btn btn-secondary" on:click={exportSettings}>
                <Icon name="download" size={14} />
                Exportar Config
            </button>
            <label class="btn btn-secondary file-input">
                <Icon name="upload" size={14} />
                Importar Config
                <input type="file" accept=".json" on:change={importSettings} hidden />
            </label>
        </div>
        <button class="btn btn-danger" on:click={resetToDefaults}>
            <Icon name="refresh-cw" size={14} />
            Restaurar por defecto
        </button>
    </section>
    
    <!-- About -->
    <section class="about-section">
        <div class="about-logo">
            <span class="logo-icon">⚡</span>
            <div class="logo-text">
                <span class="app-name">NetBoozt</span>
                <span class="app-version">v3.0.0 Tauri</span>
            </div>
        </div>
        <p class="about-desc">Network Optimization Tool for Windows</p>
        <p class="about-tech">Rust + Tauri + Svelte + TypeScript</p>
        <div class="about-links">
            <a href="https://loust.pro" target="_blank">🌐 LOUST</a>
            <a href="https://github.com/louzt/NetBoozt_InternetUpgrade" target="_blank">📦 GitHub</a>
            <a href="https://github.com/louzt/NetBoozt_InternetUpgrade/issues" target="_blank">🐛 Reportar Bug</a>
        </div>
    </section>
</div>

<style>
    .settings-page {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        height: 100%;
        overflow-y: auto;
        padding-bottom: 2rem;
    }
    
    .settings-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .header-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: var(--primary, #00d4aa);
    }
    
    .header-info h1 {
        margin: 0;
        font-size: 1.25rem;
        color: var(--text-primary, #fff);
    }
    
    .header-info p {
        margin: 0;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .settings-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 1rem;
    }
    
    .settings-card {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 1.25rem;
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        color: var(--primary, #00d4aa);
    }
    
    .card-header h2 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .setting-group {
        margin-bottom: 1rem;
    }
    
    .setting-label {
        display: block;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted, #888);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .setting-select {
        width: 100%;
        padding: 0.625rem 0.875rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        color: var(--text-primary, #fff);
        font-size: 0.875rem;
        cursor: pointer;
    }
    
    .setting-select:focus {
        outline: none;
        border-color: var(--primary, #00d4aa);
    }
    
    /* Toggle Settings */
    .toggle-setting {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .toggle-setting:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    
    .toggle-info {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }
    
    .toggle-label {
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
        font-weight: 500;
    }
    
    .toggle-desc {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .toggle-setting input[type="checkbox"] {
        width: 40px;
        height: 22px;
        accent-color: var(--primary, #00d4aa);
        cursor: pointer;
    }
    
    /* Theme Selector */
    .theme-selector {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .theme-option {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
        padding: 0.625rem 0.875rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 2px solid transparent;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .theme-option:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    
    .theme-option.active {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.1);
    }
    
    .theme-icon {
        font-size: 1.25rem;
    }
    
    .theme-name {
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    /* Color Selector */
    .color-selector {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .color-option {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: var(--color);
        border: 2px solid transparent;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .color-option:hover {
        transform: scale(1.1);
    }
    
    .color-option.active {
        border-color: #fff;
        box-shadow: 0 0 0 2px var(--color);
    }
    
    /* Profile Selector */
    .profile-selector {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .profile-option {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 2px solid transparent;
        border-radius: 8px;
        cursor: pointer;
        text-align: left;
        transition: all 0.2s;
    }
    
    .profile-option:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    
    .profile-option.active {
        border-color: var(--primary, #00d4aa);
        background: rgba(0, 212, 170, 0.1);
    }
    
    .profile-icon {
        font-size: 1.5rem;
    }
    
    .profile-info {
        display: flex;
        flex-direction: column;
    }
    
    .profile-name {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .profile-desc {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    /* Actions */
    .settings-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
    }
    
    .action-group {
        display: flex;
        gap: 0.5rem;
    }
    
    .btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: all 0.15s;
    }
    
    .btn-secondary {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-secondary, #a0a0a0);
        border: 1px solid var(--border, #3d3d3d);
    }
    
    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.1);
        color: var(--text-primary, #fff);
    }
    
    .btn-danger {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .btn-danger:hover {
        background: rgba(239, 68, 68, 0.2);
    }
    
    .file-input {
        cursor: pointer;
    }
    
    /* About Section */
    .about-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 2rem;
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        gap: 0.5rem;
    }
    
    .about-logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .logo-icon {
        font-size: 2.5rem;
    }
    
    .logo-text {
        display: flex;
        flex-direction: column;
        text-align: left;
    }
    
    .app-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary, #00d4aa);
    }
    
    .app-version {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .about-desc {
        margin: 0;
        font-size: 0.875rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .about-tech {
        margin: 0;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .about-links {
        display: flex;
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    .about-links a {
        color: var(--text-secondary, #a0a0a0);
        text-decoration: none;
        font-size: 0.8rem;
        transition: color 0.2s;
    }
    
    .about-links a:hover {
        color: var(--primary, #00d4aa);
    }
</style>
