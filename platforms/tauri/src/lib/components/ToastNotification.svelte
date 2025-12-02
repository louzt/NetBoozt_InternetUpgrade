<!--
    ToastNotification.svelte - Sistema de alertas in-app
    Muestra notificaciones toast y mantiene historial de errores
    By LOUST
-->
<script context="module" lang="ts">
    export interface Toast {
        id: string;
        type: 'success' | 'error' | 'warning' | 'info';
        title: string;
        message: string;
        timestamp: Date;
        duration?: number; // ms, 0 = persistent
    }
</script>

<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import { fade, fly } from 'svelte/transition';
    import Icon from './Icon.svelte';
    
    export let toasts: Toast[] = [];
    export let maxVisible = 3;
    export let defaultDuration = 5000;
    
    const dispatch = createEventDispatcher();
    
    function dismissToast(id: string) {
        dispatch('dismiss', id);
    }
    
    function getIcon(type: Toast['type']): string {
        const icons: Record<string, string> = {
            success: 'check',
            error: 'warning',
            warning: 'warning',
            info: 'info'
        };
        return icons[type] || 'info';
    }
    
    function getEmoji(type: Toast['type']): string {
        const emojis: Record<string, string> = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return emojis[type] || 'ℹ️';
    }
    
    // Auto-dismiss con duration
    $: visibleToasts = toasts.slice(0, maxVisible);
    
    onMount(() => {
        const interval = setInterval(() => {
            const now = Date.now();
            toasts.forEach(toast => {
                const duration = toast.duration ?? defaultDuration;
                if (duration > 0 && now - toast.timestamp.getTime() > duration) {
                    dismissToast(toast.id);
                }
            });
        }, 1000);
        
        return () => clearInterval(interval);
    });
</script>

<div class="toast-container">
    {#each visibleToasts as toast (toast.id)}
        <div 
            class="toast toast-{toast.type}"
            in:fly={{ y: -20, duration: 200 }}
            out:fade={{ duration: 150 }}
        >
            <div class="toast-icon">
                <span class="toast-emoji">{getEmoji(toast.type)}</span>
            </div>
            <div class="toast-content">
                <span class="toast-title">{toast.title}</span>
                <p class="toast-message">{toast.message}</p>
            </div>
            <button class="toast-dismiss" on:click={() => dismissToast(toast.id)}>
                <Icon name="close" size={14} />
            </button>
        </div>
    {/each}
    
    {#if toasts.length > maxVisible}
        <div class="toast-overflow">
            +{toasts.length - maxVisible} más
        </div>
    {/if}
</div>

<style>
    .toast-container {
        position: fixed;
        top: 60px;
        right: 1rem;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        max-width: 360px;
        pointer-events: none;
    }
    
    .toast {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.875rem 1rem;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid var(--border, #2d2d2d);
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        pointer-events: auto;
        position: relative;
        overflow: hidden;
    }
    
    .toast::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
    }
    
    .toast-success::before {
        background: var(--primary, #00d4aa);
    }
    
    .toast-error::before {
        background: #ff6b6b;
    }
    
    .toast-warning::before {
        background: #fdcb6e;
    }
    
    .toast-info::before {
        background: #74b9ff;
    }
    
    .toast-icon {
        flex-shrink: 0;
    }
    
    .toast-emoji {
        font-size: 1.25rem;
    }
    
    .toast-content {
        flex: 1;
        min-width: 0;
    }
    
    .toast-title {
        display: block;
        font-weight: 600;
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
        margin-bottom: 0.25rem;
    }
    
    .toast-message {
        margin: 0;
        font-size: 0.8rem;
        color: var(--text-secondary, #a0a0a0);
        line-height: 1.4;
    }
    
    .toast-dismiss {
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        padding: 0.25rem;
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.15s;
        flex-shrink: 0;
    }
    
    .toast-dismiss:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .toast-overflow {
        text-align: center;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
        padding: 0.5rem;
        pointer-events: auto;
        cursor: pointer;
    }
</style>
