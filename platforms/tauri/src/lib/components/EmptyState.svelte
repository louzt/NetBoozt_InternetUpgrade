<script lang="ts">
    /**
     * Empty State Component
     * Estado vacío que ocupa todo el espacio disponible
     */
    export let icon = '📋';
    export let title = 'Sin datos';
    export let description = '';
    export let actionText = '';
    export let onAction: (() => void) | null = null;
</script>

<div class="empty-state">
    <div class="empty-content">
        <span class="empty-icon">{icon}</span>
        <h3 class="empty-title">{title}</h3>
        {#if description}
            <p class="empty-description">{description}</p>
        {/if}
        {#if actionText && onAction}
            <button class="empty-action" on:click={onAction}>
                {actionText}
            </button>
        {/if}
    </div>
</div>

<style>
    .empty-state {
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 1;
        min-height: 400px;
        height: 100%;
        background: linear-gradient(135deg, rgba(0, 212, 170, 0.02), rgba(0, 168, 255, 0.02));
        border-radius: 16px;
        border: 2px dashed var(--border, #2d2d2d);
    }
    
    .empty-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 3rem;
        max-width: 400px;
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        opacity: 0.5;
        filter: grayscale(0.5);
    }
    
    .empty-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0 0 0.5rem 0;
    }
    
    .empty-description {
        font-size: 0.875rem;
        color: var(--text-muted, #666);
        margin: 0 0 1.5rem 0;
        line-height: 1.5;
    }
    
    .empty-action {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: var(--primary, #00d4aa);
        color: #000;
        border: none;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .empty-action:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.3);
    }
</style>
