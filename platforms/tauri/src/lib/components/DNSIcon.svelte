<!--
    DNSIcon.svelte - Iconos oficiales de proveedores DNS con fallback
    Usa logos reales de los proveedores con emoji fallback
    By LOUST
-->
<script lang="ts">
    export let provider: string;
    export let size: number = 32;
    
    // URLs de logos oficiales (CDN públicos / favicons)
    const PROVIDER_LOGOS: Record<string, { url: string; fallback: string; bg?: string }> = {
        cloudflare: {
            url: 'https://www.cloudflare.com/favicon.ico',
            fallback: '☁️',
            bg: '#F38020'
        },
        google: {
            url: 'https://www.google.com/images/branding/googleg/1x/googleg_standard_color_128dp.png',
            fallback: '🔍',
            bg: '#4285F4'
        },
        quad9: {
            url: 'https://www.quad9.net/favicon.ico',
            fallback: '🛡️',
            bg: '#2A2A72'
        },
        opendns: {
            url: 'https://www.opendns.com/favicon.ico',
            fallback: '🔐',
            bg: '#FF6600'
        },
        adguard: {
            url: 'https://adguard.com/favicon.ico',
            fallback: '🚫',
            bg: '#68BC71'
        },
        cleanbrowsing: {
            url: 'https://cleanbrowsing.org/favicon.ico',
            fallback: '🧹',
            bg: '#1E88E5'
        },
        nextdns: {
            url: 'https://nextdns.io/favicon.ico',
            fallback: '⚡',
            bg: '#5856D6'
        },
        comodo: {
            url: 'https://www.comodo.com/favicon.ico',
            fallback: '🔒',
            bg: '#006400'
        },
        norton: {
            url: 'https://www.norton.com/favicon.ico',
            fallback: '✓',
            bg: '#FFC820'
        }
    };
    
    let imageError = false;
    let imageLoaded = false;
    
    $: providerData = PROVIDER_LOGOS[provider.toLowerCase()] || { url: '', fallback: '🌐', bg: '#666' };
    
    function handleError() {
        imageError = true;
    }
    
    function handleLoad() {
        imageLoaded = true;
    }
</script>

<div 
    class="dns-icon-wrapper" 
    style="--size: {size}px; --bg-color: {providerData.bg}"
    class:loaded={imageLoaded && !imageError}
>
    {#if providerData.url && !imageError}
        <img 
            src={providerData.url} 
            alt={provider}
            width={size}
            height={size}
            on:error={handleError}
            on:load={handleLoad}
            class="dns-logo"
            class:hidden={!imageLoaded}
        />
    {/if}
    
    {#if imageError || !providerData.url || !imageLoaded}
        <span class="dns-emoji" class:fading={!imageError && providerData.url && !imageLoaded}>
            {providerData.fallback}
        </span>
    {/if}
</div>

<style>
    .dns-icon-wrapper {
        width: var(--size);
        height: var(--size);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        border-radius: 8px;
        overflow: hidden;
        flex-shrink: 0;
    }
    
    .dns-logo {
        width: 100%;
        height: 100%;
        object-fit: contain;
        transition: opacity 0.2s;
    }
    
    .dns-logo.hidden {
        opacity: 0;
        position: absolute;
    }
    
    .dns-emoji {
        font-size: calc(var(--size) * 0.6);
        line-height: 1;
        transition: opacity 0.2s;
    }
    
    .dns-emoji.fading {
        position: absolute;
    }
    
    /* Mostrar background sutil cuando tiene logo */
    .dns-icon-wrapper.loaded {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        padding: 4px;
    }
</style>
