<!--
    LogoIcon.svelte - Icono/Logo de LOUST/NetBoozt
    Usa el favicon PNG existente
    By LOUST
-->
<script lang="ts">
    export let size: number = 32;
    export let animated: boolean = false;
    export let className: string = '';
</script>

<div class="logo-icon-wrapper {className}" class:animated style="--size: {size}px">
    <img src="/favicon.png" alt="NetBoozt" class="logo-img" />
</div>

<style>
    .logo-icon-wrapper {
        width: var(--size);
        height: var(--size);
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .logo-img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        filter: drop-shadow(0 0 6px rgba(0, 212, 170, 0.3));
    }
    
    .animated .logo-img {
        animation: pulse-glow 2s ease-in-out infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% {
            filter: drop-shadow(0 0 6px rgba(0, 212, 170, 0.3));
        }
        50% {
            filter: drop-shadow(0 0 12px rgba(0, 212, 170, 0.6));
        }
    }
</style>
