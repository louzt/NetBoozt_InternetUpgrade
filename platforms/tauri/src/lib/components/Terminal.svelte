<script lang="ts">
    /**
     * Terminal Component
     * Terminal de logs integrado - usa store centralizado
     */
    import { onMount, onDestroy } from 'svelte';
    import { listen } from '$lib/tauri-bridge';
    import { terminalLogs, type LogEntry } from '$lib/stores/terminalStore';
    
    export let expanded = false;
    export let maxLines = 200;
    
    let unlistenLogs: (() => void) | null = null;
    let terminalRef: HTMLDivElement;
    let autoScroll = true;
    
    // Suscribirse al store y limitar líneas visibles
    $: visibleLogs = $terminalLogs.slice(-maxLines);
    
    onMount(async () => {
        // Escuchar logs del backend
        try {
            unlistenLogs = await listen<any>('log_entry', (event) => {
                terminalLogs.addFromEvent(event.payload);
            });
        } catch (e) {
            console.error('Error listening logs:', e);
        }
        
        // Log inicial
        terminalLogs.info('Terminal iniciada');
    });
    
    onDestroy(() => {
        if (unlistenLogs) unlistenLogs();
    });
    
    // Auto-scroll cuando cambian los logs
    $: if (autoScroll && terminalRef && visibleLogs.length > 0) {
        requestAnimationFrame(() => {
            if (terminalRef) terminalRef.scrollTop = terminalRef.scrollHeight;
        });
    }
    
    function clearLogs() {
        terminalLogs.clear();
    }
    
    function toggleAutoScroll() {
        autoScroll = !autoScroll;
    }
    
    function getLevelIcon(level: string): string {
        switch (level) {
            case 'error': return '❌';
            case 'warn': return '⚠️';
            case 'debug': return '🔍';
            case 'dryrun': return '🧪';
            default: return 'ℹ️';
        }
    }
    
    function getLevelClass(level: string): string {
        return `log-${level}`;
    }
    
    function formatTime(date: Date): string {
        return date.toLocaleTimeString();
    }
</script>

<div class="terminal" class:expanded>
    <div class="terminal-header">
        <span class="terminal-title">
            <span class="terminal-icon">💻</span>
            Logs
        </span>
        <div class="terminal-actions">
            <button 
                class="terminal-btn" 
                class:active={autoScroll}
                on:click={toggleAutoScroll}
                title={autoScroll ? 'Auto-scroll ON' : 'Auto-scroll OFF'}
            >
                ⬇️
            </button>
            <button 
                class="terminal-btn" 
                on:click={clearLogs}
                title="Limpiar logs"
            >
                🗑️
            </button>
        </div>
    </div>
    
    <div class="terminal-content" bind:this={terminalRef}>
        {#if visibleLogs.length === 0}
            <div class="terminal-empty">
                <span class="empty-icon">📋</span>
                <span>No hay logs aún...</span>
            </div>
        {:else}
            {#each visibleLogs as log (log.id)}
                <div class="log-entry {getLevelClass(log.level)}">
                    <span class="log-time">{formatTime(log.timestamp)}</span>
                    <span class="log-icon">{getLevelIcon(log.level)}</span>
                    <span class="log-message">{log.message}</span>
                </div>
            {/each}
        {/if}
    </div>
</div>

<style>
    .terminal {
        background: #0d0d0d;
        border-top: 1px solid #2d2d2d;
        display: flex;
        flex-direction: column;
        height: 120px;
        transition: height 0.3s ease;
    }
    
    .terminal.expanded {
        height: 300px;
    }
    
    .terminal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0.75rem;
        background: #151515;
        border-bottom: 1px solid #2d2d2d;
    }
    
    .terminal-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.7rem;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .terminal-icon {
        font-size: 0.8rem;
    }
    
    .terminal-actions {
        display: flex;
        gap: 0.25rem;
    }
    
    .terminal-btn {
        background: transparent;
        border: none;
        padding: 0.25rem;
        cursor: pointer;
        opacity: 0.5;
        font-size: 0.7rem;
        border-radius: 4px;
        transition: all 0.15s;
    }
    
    .terminal-btn:hover {
        opacity: 1;
        background: #2d2d2d;
    }
    
    .terminal-btn.active {
        opacity: 1;
        background: rgba(0, 212, 170, 0.2);
    }
    
    .terminal-content {
        flex: 1;
        overflow-y: auto;
        padding: 0.5rem;
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 0.65rem;
        line-height: 1.5;
    }
    
    .terminal-content::-webkit-scrollbar {
        width: 6px;
    }
    
    .terminal-content::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .terminal-content::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 3px;
    }
    
    .terminal-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #555;
        gap: 0.5rem;
    }
    
    .empty-icon {
        font-size: 1.5rem;
        opacity: 0.5;
    }
    
    .log-entry {
        display: flex;
        gap: 0.5rem;
        padding: 0.125rem 0;
        color: #aaa;
    }
    
    .log-time {
        color: #555;
        min-width: 60px;
    }
    
    .log-icon {
        font-size: 0.7rem;
    }
    
    .log-message {
        flex: 1;
        word-break: break-word;
    }
    
    .log-error {
        color: #ff6b6b;
    }
    
    .log-warn {
        color: #fdcb6e;
    }
    
    .log-debug {
        color: #74b9ff;
    }
    
    .log-info {
        color: #00d4aa;
    }
    
    .log-dryrun {
        color: #fdcb6e;
        background: rgba(253, 203, 110, 0.05);
        padding: 0.125rem 0.25rem;
        border-radius: 2px;
        margin: 0.125rem 0;
    }
    
    .log-dryrun .log-message {
        font-family: 'JetBrains Mono', monospace;
    }
</style>
