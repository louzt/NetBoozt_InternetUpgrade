<!--
    FloatingTerminal.svelte - Terminal integrada con drag resize
    Se integra al layout, sidebar por encima
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import Icon from './Icon.svelte';
    import Terminal from './Terminal.svelte';
    import { errorAlerts, alerts } from '$lib/stores/alertStore';
    
    export let show = false;
    export let height = 300; // altura por defecto más grande
    export let sidebarWidth = 220; // ancho de sidebar para offset
    export let activeTab: 'terminal' | 'problems' = 'terminal'; // Pestaña activa
    
    const dispatch = createEventDispatcher();
    
    // Tabs disponibles
    type TabType = 'terminal' | 'problems';
    const tabs: { id: TabType; label: string; icon: string }[] = [
        { id: 'terminal', label: 'Terminal', icon: 'terminal' },
        { id: 'problems', label: 'Problemas', icon: 'alert-triangle' }
    ];
    
    function setTab(tab: TabType) {
        activeTab = tab;
        dispatch('tabChange', tab);
    }
    
    function dismissError(id: string) {
        alerts.dismiss(id);
    }
    
    function clearAllErrors() {
        $errorAlerts.forEach(e => alerts.dismiss(e.id));
    }
    
    let isResizing = false;
    let isDragging = false;
    let startY = 0;
    let startHeight = 0;
    let dragThreshold = 80; // Si arrastra más de 80px hacia abajo, cierra
    
    function toggleTerminal() {
        dispatch('toggle');
    }
    
    function startResize(e: MouseEvent) {
        e.preventDefault();
        isResizing = true;
        isDragging = true;
        startY = e.clientY;
        startHeight = height;
        window.addEventListener('mousemove', handleResize);
        window.addEventListener('mouseup', stopResize);
    }
    
    function handleResize(e: MouseEvent) {
        if (!isResizing) return;
        const delta = startY - e.clientY;
        const newHeight = startHeight + delta;
        
        // Si arrastra hacia abajo más del threshold, cerrar
        if (delta < -dragThreshold) {
            stopResize();
            dispatch('toggle');
            return;
        }
        
        height = Math.min(Math.max(200, newHeight), 600);
    }
    
    function stopResize() {
        isResizing = false;
        isDragging = false;
        window.removeEventListener('mousemove', handleResize);
        window.removeEventListener('mouseup', stopResize);
    }
</script>

<div 
    class="terminal-panel" 
    class:show 
    class:dragging={isDragging}
    style="--terminal-height: {height}px; --sidebar-offset: {sidebarWidth}px"
>
    <!-- Drag Handle / Header -->
    <button 
        type="button"
        class="terminal-header"
        on:mousedown={startResize}
        aria-label="Arrastrar para redimensionar o cerrar"
    >
        <div class="drag-indicator">
            <span class="drag-line"></span>
        </div>
        <div class="header-content">
            <div class="header-left">
                <!-- Tabs -->
                {#each tabs as tab}
                    <button 
                        class="tab-btn"
                        class:active={activeTab === tab.id}
                        on:click|stopPropagation={() => setTab(tab.id)}
                    >
                        <Icon name={tab.icon} size={14} />
                        <span>{tab.label}</span>
                        {#if tab.id === 'problems' && $errorAlerts.length > 0}
                            <span class="tab-badge">{$errorAlerts.length}</span>
                        {/if}
                    </button>
                {/each}
            </div>
            <div class="header-actions">
                {#if activeTab === 'problems' && $errorAlerts.length > 0}
                    <button class="header-btn clear-btn" on:click|stopPropagation={clearAllErrors} title="Limpiar todo">
                        <Icon name="trash" size={14} />
                    </button>
                {/if}
                <button class="header-btn" on:click|stopPropagation={toggleTerminal} title="Minimizar">
                    <Icon name="chevron-down" size={14} />
                </button>
            </div>
        </div>
    </button>
    
    <!-- Content based on tab -->
    <div class="terminal-wrapper">
        {#if activeTab === 'terminal'}
            <Terminal maxLines={200} />
        {:else if activeTab === 'problems'}
            <div class="problems-panel">
                {#if $errorAlerts.length === 0}
                    <div class="empty-problems">
                        <Icon name="check-circle" size={48} />
                        <h3>Sin problemas</h3>
                        <p>No se han detectado errores o advertencias</p>
                    </div>
                {:else}
                    <div class="problems-list">
                        {#each $errorAlerts as error (error.id)}
                            <div class="problem-item" class:error={error.type === 'error'} class:warning={error.type === 'warning'}>
                                <div class="problem-icon">
                                    <Icon name={error.type === 'error' ? 'x-circle' : 'alert-triangle'} size={16} />
                                </div>
                                <div class="problem-content">
                                    <span class="problem-title">{error.title}</span>
                                    <span class="problem-message">{error.message}</span>
                                    <span class="problem-time">{new Date(error.timestamp).toLocaleTimeString()}</span>
                                </div>
                                <button class="problem-dismiss" on:click={() => dismissError(error.id)} title="Descartar">
                                    <Icon name="x" size={14} />
                                </button>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</div>

<!-- Tab para abrir cuando está cerrado - con tabs integrados -->
{#if !show}
    <div class="terminal-tabs-bar" style="--sidebar-offset: {sidebarWidth}px">
        <button 
            class="tab-toggle" 
            class:active={activeTab === 'terminal'}
            on:click={() => { activeTab = 'terminal'; toggleTerminal(); }}
        >
            <Icon name="terminal" size={14} />
            <span>Terminal</span>
        </button>
        <div class="tab-divider"></div>
        <button 
            class="tab-toggle"
            class:active={activeTab === 'problems'}
            on:click={() => { activeTab = 'problems'; toggleTerminal(); }}
        >
            <Icon name="alert-triangle" size={14} />
            <span>Problemas</span>
            {#if $errorAlerts.length > 0}
                <span class="mini-badge">{$errorAlerts.length}</span>
            {/if}
        </button>
        <span class="expand-hint">
            <Icon name="chevron-up" size={12} />
        </span>
    </div>
{/if}

<style>
    .terminal-panel {
        position: fixed;
        bottom: 0;
        left: var(--sidebar-offset);
        right: 0;
        height: var(--terminal-height);
        background: #0d0d0d;
        border-top: 1px solid var(--border, #2d2d2d);
        display: flex;
        flex-direction: column;
        z-index: 50;
        transform: translateY(100%);
        transition: transform 0.25s ease;
    }
    
    .terminal-panel.show {
        transform: translateY(0);
    }
    
    .terminal-panel.dragging {
        transition: none;
    }
    
    .terminal-header {
        display: flex;
        flex-direction: column;
        background: #151515;
        cursor: ns-resize;
        user-select: none;
        /* Reset button styles */
        border: none;
        padding: 0;
        margin: 0;
        width: 100%;
        font: inherit;
        color: inherit;
        text-align: left;
    }
    
    .drag-indicator {
        display: flex;
        justify-content: center;
        padding: 0.35rem 0;
    }
    
    .drag-line {
        width: 40px;
        height: 4px;
        background: var(--border, #3d3d3d);
        border-radius: 2px;
        transition: all 0.15s;
    }
    
    .terminal-header:hover .drag-line,
    .dragging .drag-line {
        background: var(--primary, #00d4aa);
        width: 60px;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        border-top: 1px solid var(--border, #2d2d2d);
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .tab-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: transparent;
        border: none;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8125rem;
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.15s;
    }
    
    .tab-btn:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .tab-btn.active {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--primary, #00d4aa);
    }
    
    .tab-badge {
        background: var(--error, #ff4444);
        color: white;
        font-size: 0.65rem;
        font-weight: 600;
        padding: 0.1rem 0.35rem;
        border-radius: 8px;
        min-width: 1rem;
        text-align: center;
    }
    
    .header-actions {
        display: flex;
        gap: 0.25rem;
    }
    
    .header-btn {
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        padding: 0.35rem;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .header-btn:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .header-btn.clear-btn:hover {
        background: rgba(255, 68, 68, 0.15);
        color: var(--error, #ff4444);
    }
    
    .terminal-wrapper {
        flex: 1;
        overflow: hidden;
    }
    
    /* Problems Panel */
    .problems-panel {
        height: 100%;
        overflow-y: auto;
        background: #0d0d0d;
    }
    
    .empty-problems {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: var(--text-muted, #666);
        gap: 0.5rem;
    }
    
    .empty-problems h3 {
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .empty-problems p {
        margin: 0;
        font-size: 0.8125rem;
    }
    
    .problems-list {
        display: flex;
        flex-direction: column;
    }
    
    .problem-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border, #2d2d2d);
        transition: background 0.15s;
    }
    
    .problem-item:hover {
        background: rgba(255, 255, 255, 0.02);
    }
    
    .problem-item.error .problem-icon {
        color: var(--error, #ff4444);
    }
    
    .problem-item.warning .problem-icon {
        color: var(--warning, #ffaa00);
    }
    
    .problem-icon {
        flex-shrink: 0;
        padding-top: 0.1rem;
    }
    
    .problem-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        min-width: 0;
    }
    
    .problem-title {
        font-size: 0.8125rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .problem-message {
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
        line-height: 1.4;
    }
    
    .problem-time {
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
    }
    
    .problem-dismiss {
        flex-shrink: 0;
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        padding: 0.25rem;
        border-radius: 4px;
        cursor: pointer;
        opacity: 0;
        transition: all 0.15s;
    }
    
    .problem-item:hover .problem-dismiss {
        opacity: 1;
    }
    
    .problem-dismiss:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    /* Tab flotante cuando está cerrado - tabs integrados */
    .terminal-tabs-bar {
        position: fixed;
        bottom: 0;
        left: calc(var(--sidebar-offset) + 50%);
        transform: translateX(-50%);
        display: flex;
        align-items: center;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid var(--border, #2d2d2d);
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        z-index: 50;
        overflow: hidden;
    }
    
    .tab-toggle {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.5rem 1rem;
        background: transparent;
        border: none;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8125rem;
        cursor: pointer;
        transition: all 0.15s;
    }
    
    .tab-toggle:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .tab-toggle.active {
        color: var(--primary, #00d4aa);
    }
    
    .tab-divider {
        width: 1px;
        height: 1.25rem;
        background: var(--border, #2d2d2d);
    }
    
    .mini-badge {
        background: var(--error, #ff4444);
        color: white;
        font-size: 0.6rem;
        font-weight: 600;
        padding: 0.1rem 0.3rem;
        border-radius: 6px;
        min-width: 0.875rem;
        text-align: center;
    }
    
    .expand-hint {
        color: var(--text-muted, #666);
        margin-left: 0.25rem;
        margin-right: 0.5rem;
        display: flex;
        align-items: center;
    }
</style>
