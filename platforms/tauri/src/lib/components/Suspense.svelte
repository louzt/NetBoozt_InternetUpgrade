<!--
    Suspense.svelte - Componente similar a React Suspense
    Muestra fallback mientras el contenido carga
    
    By LOUST (www.loust.pro)
-->
<script lang="ts">
    export let loading: boolean = true;
    export let delay: number = 0; // Delay antes de mostrar skeleton (evita flash)
    export let minDuration: number = 300; // Duración mínima del skeleton
    
    let showFallback = false;
    let loadStartTime = 0;
    
    $: if (loading) {
        loadStartTime = Date.now();
        if (delay > 0) {
            setTimeout(() => {
                if (loading) showFallback = true;
            }, delay);
        } else {
            showFallback = true;
        }
    } else {
        // Asegurar duración mínima para evitar flash
        const elapsed = Date.now() - loadStartTime;
        if (elapsed < minDuration && showFallback) {
            setTimeout(() => {
                showFallback = false;
            }, minDuration - elapsed);
        } else {
            showFallback = false;
        }
    }
</script>

{#if loading && showFallback}
    <div class="suspense-fallback">
        <slot name="fallback">
            <!-- Default fallback -->
            <div class="default-fallback">
                <div class="spinner"></div>
                <span>Cargando...</span>
            </div>
        </slot>
    </div>
{:else if !loading}
    <slot />
{/if}

<style>
    .suspense-fallback {
        width: 100%;
        min-height: inherit;
    }
    
    .default-fallback {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        gap: 1rem;
        color: var(--text-muted, #666);
    }
    
    .spinner {
        width: 32px;
        height: 32px;
        border: 3px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
