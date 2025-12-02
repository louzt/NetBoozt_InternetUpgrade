<script lang="ts">
    /**
     * NetBoozt - Alert Toast Component
     * Notificación toast para alertas
     * 
     * By LOUST (www.loust.pro)
     */
    
    import { fly, fade } from 'svelte/transition';
    
    export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
    export let message: string;
    export let duration: number = 3000;
    export let dismissible: boolean = true;
    export let onClose: () => void = () => {};
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    let visible = true;
    
    if (duration > 0) {
        setTimeout(() => {
            visible = false;
            onClose();
        }, duration);
    }
    
    function dismiss() {
        visible = false;
        onClose();
    }
</script>

{#if visible}
    <div 
        class="toast {type}"
        in:fly={{ y: -20, duration: 200 }}
        out:fade={{ duration: 150 }}
        role="alert"
    >
        <span class="toast-icon">{icons[type]}</span>
        <span class="toast-message">{message}</span>
        {#if dismissible}
            <button class="toast-close" on:click={dismiss} aria-label="Cerrar">
                ✕
            </button>
        {/if}
    </div>
{/if}

<style>
    .toast {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.875rem 1rem;
        border-radius: 10px;
        background: var(--bg-card, #2b2b2b);
        border-left: 4px solid;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        max-width: 400px;
    }
    
    .toast.success {
        border-color: var(--success, #00ff88);
        background: rgba(0, 255, 136, 0.1);
    }
    
    .toast.error {
        border-color: var(--error, #ff6b6b);
        background: rgba(255, 107, 107, 0.1);
    }
    
    .toast.warning {
        border-color: var(--warning, #fdcb6e);
        background: rgba(253, 203, 110, 0.1);
    }
    
    .toast.info {
        border-color: var(--info, #00a8ff);
        background: rgba(0, 168, 255, 0.1);
    }
    
    .toast-icon {
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    
    .toast-message {
        flex: 1;
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
        line-height: 1.4;
    }
    
    .toast-close {
        background: none;
        border: none;
        color: var(--text-muted, #888);
        cursor: pointer;
        padding: 0.25rem;
        font-size: 0.875rem;
        border-radius: 4px;
        transition: all 0.15s;
    }
    
    .toast-close:hover {
        background: var(--bg-elevated, #333);
        color: var(--text-primary, #fff);
    }
</style>
