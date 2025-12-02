<!--
    CollapsibleSidebar.svelte - Sidebar colapsable con logo animado
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import AnimatedLogo from './AnimatedLogo.svelte';
    import LogoIcon from './LogoIcon.svelte';
    import Icon from './Icon.svelte';
    import { errorCount } from '../stores/alertStore';
    
    export let activeTab = 'dashboard';
    export let collapsed = false;
    export let monitoringActive = false;
    export let uptime = 0;
    export let alerts: any[] = [];
    
    const dispatch = createEventDispatcher();
    
    type TabType = 'dashboard' | 'dns' | 'monitor' | 'alerts' | 'settings' | 'docs' | 'github' | 'problems' | 'reports';
    
    const navItems: { id: TabType; icon: string; label: string }[] = [
        { id: 'dashboard', icon: 'dashboard', label: 'Dashboard' },
        { id: 'dns', icon: 'globe', label: 'DNS' },
        { id: 'monitor', icon: 'activity', label: 'Monitor' },
        { id: 'reports', icon: 'clipboard-list', label: 'Reportes' },
        { id: 'alerts', icon: 'bell', label: 'Alertas' },
        { id: 'docs', icon: 'book-open', label: 'Docs' },
        { id: 'github', icon: 'github', label: 'GitHub' },
        { id: 'settings', icon: 'settings', label: 'Config' }
    ];
    
    function formatUptime(s: number): string {
        const h = Math.floor(s / 3600);
        const m = Math.floor((s % 3600) / 60);
        const sec = s % 60;
        return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${sec.toString().padStart(2,'0')}`;
    }
    
    function setTab(tab: TabType) {
        dispatch('tabChange', tab);
    }
    
    function openProblems() {
        dispatch('openProblems');
    }
    
    $: unresolvedAlerts = alerts.filter(a => !a.resolved).length;
</script>

<aside class="sidebar" class:collapsed>
    <!-- Collapse Toggle -->
    <button class="collapse-btn" on:click={() => dispatch('toggleCollapse')} aria-label={collapsed ? 'Expandir sidebar' : 'Colapsar sidebar'}>
        <Icon name={collapsed ? 'chevron-right' : 'chevron-left'} size={12} />
    </button>
    
    <!-- Logo -->
    <div class="logo-section">
        <LogoIcon size={collapsed ? 28 : 32} />
        {#if !collapsed}
            <AnimatedLogo collapsed={false} />
        {/if}
    </div>
    
    <!-- Navigation -->
    <nav class="nav">
        {#each navItems as item}
            <button 
                class="nav-item" 
                class:active={activeTab === item.id} 
                on:click={() => setTab(item.id)}
                title={collapsed ? item.label : ''}
            >
                <Icon name={item.icon} size={18} strokeWidth={activeTab === item.id ? 2 : 1.5} />
                {#if !collapsed}
                    <span class="nav-label">{item.label}</span>
                {/if}
                {#if item.id === 'alerts' && unresolvedAlerts > 0}
                    <span class="badge">{unresolvedAlerts}</span>
                {/if}
            </button>
        {/each}
    </nav>
    
    <!-- Problems Button (above status) -->
    {#if $errorCount > 0}
        <button class="problems-btn" on:click={openProblems} title="Ver errores detectados">
            <Icon name="warning" size={16} />
            {#if !collapsed}
                <span class="problems-text">Problemas</span>
            {/if}
            <span class="problems-count">{$errorCount}</span>
        </button>
    {/if}
    
    <!-- Status -->
    <div class="sidebar-status">
        <div class="status-indicator" class:active={monitoringActive}>
            <span class="status-dot"></span>
            {#if !collapsed}
                <span>{monitoringActive ? 'Monitoreando' : 'Detenido'}</span>
            {/if}
        </div>
        {#if monitoringActive && !collapsed}
            <span class="uptime-display">{formatUptime(uptime)}</span>
        {/if}
    </div>
    
    <!-- Footer -->
    <div class="sidebar-footer">
        {#if collapsed}
            <span class="version-small">3.0</span>
        {:else}
            <span class="version">v3.0.0</span>
            <a href="https://loust.pro" target="_blank" rel="noopener">By LOUST</a>
        {/if}
    </div>
</aside>

<style>
    .sidebar {
        width: 220px;
        background: var(--bg-card, #1a1a1a);
        display: flex;
        flex-direction: column;
        border-right: 1px solid var(--border, #2d2d2d);
        position: relative;
        transition: width 0.2s ease;
    }
    
    .sidebar.collapsed {
        width: 60px;
    }
    
    .collapse-btn {
        position: absolute;
        top: 50%;
        right: -14px;
        transform: translateY(-50%);
        width: 14px;
        height: 48px;
        border-radius: 0 6px 6px 0;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-left: none;
        color: var(--text-muted, #666);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
        transition: all 0.2s;
    }
    
    .collapse-btn:hover {
        background: var(--primary, #00d4aa);
        color: #000;
        width: 18px;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1.25rem;
        border-bottom: 1px solid var(--border, #2d2d2d);
        overflow: hidden;
    }
    
    .collapsed .logo-section {
        justify-content: center;
        padding: 1rem 0.5rem;
    }
    
    .nav {
        flex: 1;
        padding: 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        overflow-y: auto;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: transparent;
        color: var(--text-secondary, #a0a0a0);
        border-radius: 8px;
        font-size: 0.875rem;
        text-align: left;
        transition: all 0.15s;
        position: relative;
        border: none;
        cursor: pointer;
        width: 100%;
    }
    
    .collapsed .nav-item {
        justify-content: center;
        padding: 0.75rem 0.5rem;
    }
    
    .nav-item:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .nav-item.active {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    .nav-label {
        white-space: nowrap;
        overflow: hidden;
    }
    
    .badge {
        position: absolute;
        right: 0.75rem;
        background: var(--error, #ff6b6b);
        color: #fff;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.15rem 0.4rem;
        border-radius: 10px;
    }
    
    .collapsed .badge {
        right: 0.25rem;
        top: 0.25rem;
    }
    
    /* Problems Button */
    .problems-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0 0.75rem;
        padding: 0.625rem 0.75rem;
        background: rgba(255, 107, 107, 0.15);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 8px;
        color: #ff6b6b;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .collapsed .problems-btn {
        justify-content: center;
        margin: 0 0.5rem;
        padding: 0.625rem;
    }
    
    .problems-btn:hover {
        background: rgba(255, 107, 107, 0.25);
        border-color: #ff6b6b;
    }
    
    .problems-text {
        flex: 1;
        text-align: left;
    }
    
    .problems-count {
        background: #ff6b6b;
        color: #fff;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 0.15rem 0.4rem;
        border-radius: 8px;
        min-width: 18px;
        text-align: center;
    }
    
    .sidebar-status {
        padding: 0.75rem 1rem;
        border-top: 1px solid var(--border, #2d2d2d);
    }
    
    .collapsed .sidebar-status {
        padding: 0.75rem 0.5rem;
        text-align: center;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .collapsed .status-indicator {
        justify-content: center;
    }
    
    .status-indicator.active {
        color: var(--success, #00ff88);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--text-muted, #666);
        flex-shrink: 0;
    }
    
    .status-indicator.active .status-dot {
        background: var(--success, #00ff88);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .uptime-display {
        font-size: 0.7rem;
        font-family: monospace;
        color: var(--text-muted, #666);
        margin-top: 0.25rem;
        display: block;
    }
    
    .sidebar-footer {
        padding: 0.75rem 1rem;
        border-top: 1px solid var(--border, #2d2d2d);
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        display: flex;
        justify-content: space-between;
    }
    
    .collapsed .sidebar-footer {
        justify-content: center;
        padding: 0.75rem 0.5rem;
    }
    
    .sidebar-footer a {
        color: var(--primary, #00d4aa);
        text-decoration: none;
    }
    
    .version-small {
        font-size: 0.625rem;
    }
</style>
