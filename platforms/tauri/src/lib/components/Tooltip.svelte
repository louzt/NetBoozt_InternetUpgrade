<script lang="ts">
    /**
     * Tooltip Component
     * Muestra información contextual al hacer hover
     */
    export let text: string;
    export let position: 'top' | 'bottom' | 'left' | 'right' = 'top';
    export let delay: number = 300;
    
    let visible = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    
    function showTooltip() {
        timeoutId = setTimeout(() => {
            visible = true;
        }, delay);
    }
    
    function hideTooltip() {
        if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
        visible = false;
    }
</script>

<div class="tooltip-wrapper" 
    on:mouseenter={showTooltip} 
    on:mouseleave={hideTooltip}
    on:focus={showTooltip}
    on:blur={hideTooltip}
    role="tooltip"
>
    <slot />
    {#if visible && text}
        <div class="tooltip tooltip-{position}">
            {text}
            <div class="tooltip-arrow"></div>
        </div>
    {/if}
</div>

<style>
    .tooltip-wrapper {
        position: relative;
        display: inline-flex;
    }
    
    .tooltip {
        position: absolute;
        background: rgba(0, 0, 0, 0.9);
        color: #fff;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        white-space: nowrap;
        z-index: 1000;
        pointer-events: none;
        animation: fadeIn 0.15s ease-out;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 300px;
        white-space: normal;
        text-align: left;
    }
    
    .tooltip-top {
        bottom: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
    }
    
    .tooltip-bottom {
        top: calc(100% + 8px);
        left: 50%;
        transform: translateX(-50%);
    }
    
    .tooltip-left {
        right: calc(100% + 8px);
        top: 50%;
        transform: translateY(-50%);
    }
    
    .tooltip-right {
        left: calc(100% + 8px);
        top: 50%;
        transform: translateY(-50%);
    }
    
    .tooltip-arrow {
        position: absolute;
        width: 8px;
        height: 8px;
        background: rgba(0, 0, 0, 0.9);
        transform: rotate(45deg);
    }
    
    .tooltip-top .tooltip-arrow {
        bottom: -4px;
        left: 50%;
        margin-left: -4px;
    }
    
    .tooltip-bottom .tooltip-arrow {
        top: -4px;
        left: 50%;
        margin-left: -4px;
    }
    
    .tooltip-left .tooltip-arrow {
        right: -4px;
        top: 50%;
        margin-top: -4px;
    }
    
    .tooltip-right .tooltip-arrow {
        left: -4px;
        top: 50%;
        margin-top: -4px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-50%) translateY(4px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
</style>
