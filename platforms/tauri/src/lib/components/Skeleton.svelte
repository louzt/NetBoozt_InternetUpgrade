<!--
    Skeleton.svelte - Componente base para estados de carga
    Similar a Suspense de React pero para Svelte
    
    By LOUST (www.loust.pro)
-->
<script lang="ts">
    export let variant: 'text' | 'circular' | 'rectangular' | 'rounded' = 'text';
    export let width: string = '100%';
    export let height: string = '1rem';
    export let animation: 'pulse' | 'wave' | 'none' = 'wave';
    export let lines: number = 1;
    export let gap: string = '0.5rem';
</script>

{#if lines > 1}
    <div class="skeleton-lines" style="gap: {gap};">
        {#each Array(lines) as _, i}
            <div 
                class="skeleton skeleton-{variant} animation-{animation}"
                style="width: {i === lines - 1 ? '60%' : width}; height: {height};"
            ></div>
        {/each}
    </div>
{:else}
    <div 
        class="skeleton skeleton-{variant} animation-{animation}"
        style="width: {width}; height: {height};"
    ></div>
{/if}

<style>
    .skeleton {
        background: var(--skeleton-bg, #2b2b2b);
        position: relative;
        overflow: hidden;
    }
    
    .skeleton-lines {
        display: flex;
        flex-direction: column;
    }
    
    .skeleton-text {
        border-radius: 4px;
    }
    
    .skeleton-circular {
        border-radius: 50%;
    }
    
    .skeleton-rectangular {
        border-radius: 0;
    }
    
    .skeleton-rounded {
        border-radius: 12px;
    }
    
    /* Pulse animation */
    .animation-pulse {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.4;
        }
    }
    
    /* Wave animation (shimmer effect) */
    .animation-wave::after {
        content: '';
        position: absolute;
        inset: 0;
        transform: translateX(-100%);
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.08),
            transparent
        );
        animation: wave 1.5s infinite;
    }
    
    @keyframes wave {
        100% {
            transform: translateX(100%);
        }
    }
    
    .animation-none {
        animation: none;
    }
    
    .animation-none::after {
        display: none;
    }
</style>
