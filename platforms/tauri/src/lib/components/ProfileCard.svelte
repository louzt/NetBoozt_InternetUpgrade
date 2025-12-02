<script lang="ts">
    /**
     * NetBoozt - Profile Card Component
     * Tarjeta de perfil de optimización con tooltips informativos
     * 
     * By LOUST (www.loust.pro)
     */
    
    export let name: string;
    export let icon: string = '⚡';
    export let color: 'green' | 'yellow' | 'red' = 'green';
    export let description: string = '';
    export let features: string[] = [];
    export let recommended: boolean = false;
    export let loading: boolean = false;
    export let disabled: boolean = false;
    export let active: boolean = false;
    export let compact: boolean = false;
    export let onApply: () => void = () => {};
    
    // Información detallada de cada optimización para tooltips
    const optimizationInfo: Record<string, { 
        name: string;
        casual: string;  // Descripción para usuarios casuales
        technical: string; // Descripción técnica
        impact: 'speed' | 'stability' | 'latency' | 'all';
    }> = {
        'RSS': {
            name: 'Receive Side Scaling',
            casual: 'Usa todos los núcleos de tu CPU para procesar datos de red más rápido',
            technical: 'Distribuye el procesamiento de paquetes entrantes entre múltiples CPUs usando hashing de conexiones',
            impact: 'speed'
        },
        'RSC': {
            name: 'Receive Segment Coalescing', 
            casual: 'Agrupa paquetes pequeños en uno grande para menos trabajo del CPU',
            technical: 'Combina múltiples segmentos TCP en uno solo, reduciendo interrupciones y overhead',
            impact: 'speed'
        },
        'Autotuning': {
            name: 'Window Auto-Tuning',
            casual: 'Ajusta automáticamente el tamaño del buffer para mejor velocidad',
            technical: 'Ajusta dinámicamente la ventana de recepción TCP hasta 16MB según RTT y ancho de banda',
            impact: 'speed'
        },
        'ECN': {
            name: 'Explicit Congestion Notification',
            casual: 'Detecta congestión en la red ANTES de perder paquetes',
            technical: 'RFC 3168: Routers señalan congestión via IP header en lugar de dropear paquetes',
            impact: 'stability'
        },
        '+ECN': {
            name: 'Explicit Congestion Notification',
            casual: 'Detecta congestión en la red ANTES de perder paquetes',
            technical: 'RFC 3168: Routers señalan congestión via IP header en lugar de dropear paquetes',
            impact: 'stability'
        },
        'HyStart++': {
            name: 'Hybrid Slow Start',
            casual: 'Acelera más inteligente al inicio sin saturar tu conexión',
            technical: 'Sale del slow-start antes de causar pérdidas, similar al comportamiento de BBR',
            impact: 'latency'
        },
        '+HyStart++': {
            name: 'Hybrid Slow Start',
            casual: 'Acelera más inteligente al inicio sin saturar tu conexión',
            technical: 'Sale del slow-start antes de causar pérdidas, similar al comportamiento de BBR',
            impact: 'latency'
        },
        'PRR': {
            name: 'Proportional Rate Reduction',
            casual: 'Se recupera más suave después de problemas de red',
            technical: 'RFC 6937: Recuperación gradual de pérdidas en lugar de reducir 50% (Reno)',
            impact: 'stability'
        },
        '+PRR': {
            name: 'Proportional Rate Reduction',
            casual: 'Se recupera más suave después de problemas de red',
            technical: 'RFC 6937: Recuperación gradual de pérdidas en lugar de reducir 50% (Reno)',
            impact: 'stability'
        },
        'TFO': {
            name: 'TCP Fast Open',
            casual: 'Envía datos más rápido al conectar (ahorra tiempo)',
            technical: 'RFC 7413: Envía datos en el SYN, ahorra 1 RTT en conexiones repetidas',
            impact: 'latency'
        },
        '+TFO': {
            name: 'TCP Fast Open',
            casual: 'Envía datos más rápido al conectar (ahorra tiempo)',
            technical: 'RFC 7413: Envía datos en el SYN, ahorra 1 RTT en conexiones repetidas',
            impact: 'latency'
        },
        'TCP Fast Open': {
            name: 'TCP Fast Open',
            casual: 'Envía datos más rápido al conectar (ahorra tiempo)',
            technical: 'RFC 7413: Envía datos en el SYN, ahorra 1 RTT en conexiones repetidas',
            impact: 'latency'
        },
        'Pacing': {
            name: 'TCP Pacing',
            casual: 'Envía datos de forma uniforme, evita atascos',
            technical: 'Distribuye paquetes uniformemente en el tiempo, reduce bufferbloat (técnica clave de BBR)',
            impact: 'latency'
        },
        '+Pacing': {
            name: 'TCP Pacing',
            casual: 'Envía datos de forma uniforme, evita atascos',
            technical: 'Distribuye paquetes uniformemente en el tiempo, reduce bufferbloat (técnica clave de BBR)',
            impact: 'latency'
        },
        'TCP Pacing': {
            name: 'TCP Pacing',
            casual: 'Envía datos de forma uniforme, evita atascos',
            technical: 'Distribuye paquetes uniformemente en el tiempo, reduce bufferbloat (técnica clave de BBR)',
            impact: 'latency'
        },
        'RTO': {
            name: 'Initial Retransmission Timeout',
            casual: 'Detecta problemas más rápido (1s vs 3s por defecto)',
            technical: 'Reduce InitialRTO de 3000ms a 1000ms para detección más rápida de pérdidas',
            impact: 'latency'
        },
        '+RTO': {
            name: 'Initial Retransmission Timeout',
            casual: 'Detecta problemas más rápido (1s vs 3s por defecto)',
            technical: 'Reduce InitialRTO de 3000ms a 1000ms para detección más rápida de pérdidas',
            impact: 'latency'
        },
        'Initial RTO reducido': {
            name: 'Initial Retransmission Timeout',
            casual: 'Detecta problemas más rápido (1s vs 3s por defecto)',
            technical: 'Reduce InitialRTO de 3000ms a 1000ms para detección más rápida de pérdidas',
            impact: 'latency'
        },
        'Todo lo anterior': {
            name: 'Incluye todas las anteriores',
            casual: 'Incluye todas las optimizaciones del perfil anterior',
            technical: 'Hereda la configuración completa del perfil previo',
            impact: 'all'
        },
        'RSS habilitado': {
            name: 'Receive Side Scaling',
            casual: 'Usa todos los núcleos de tu CPU para procesar datos de red más rápido',
            technical: 'Distribuye el procesamiento de paquetes entrantes entre múltiples CPUs usando hashing de conexiones',
            impact: 'speed'
        },
        'RSC habilitado': {
            name: 'Receive Segment Coalescing',
            casual: 'Agrupa paquetes pequeños en uno grande para menos trabajo del CPU',
            technical: 'Combina múltiples segmentos TCP en uno solo, reduciendo interrupciones y overhead',
            impact: 'speed'
        },
        'Autotuning normal': {
            name: 'Window Auto-Tuning (Normal)',
            casual: 'Ajusta automáticamente el tamaño del buffer para mejor velocidad',
            technical: 'Nivel normal: ventana hasta 16MB. Experimental permite valores mayores',
            impact: 'speed'
        },
        'ECN habilitado': {
            name: 'Explicit Congestion Notification',
            casual: 'Detecta congestión en la red ANTES de perder paquetes',
            technical: 'RFC 3168: Routers señalan congestión via IP header en lugar de dropear paquetes',
            impact: 'stability'
        },
    };
    
    const colorMap = {
        green: { bg: 'rgba(0, 212, 170, 0.1)', border: '#00d4aa' },
        yellow: { bg: 'rgba(253, 203, 110, 0.1)', border: '#fdcb6e' },
        red: { bg: 'rgba(255, 107, 107, 0.1)', border: '#ff6b6b' }
    };
    
    const impactIcons: Record<string, string> = {
        speed: '🚀',
        stability: '🛡️',
        latency: '⚡',
        all: '✨'
    };
    
    let activeTooltip: string | null = null;
    
    function showTooltip(feature: string) {
        activeTooltip = feature;
    }
    
    function hideTooltip() {
        activeTooltip = null;
    }
    
    function toggleTooltip(feature: string) {
        activeTooltip = activeTooltip === feature ? null : feature;
    }
    
    function getFeatureInfo(feature: string) {
        return optimizationInfo[feature] || null;
    }
    
    function hasInfo(feature: string): boolean {
        return optimizationInfo[feature] !== undefined;
    }
</script>

<div 
    class="profile-card" 
    class:recommended
    class:active
    class:compact
    style="--accent-bg: {colorMap[color].bg}; --accent-border: {colorMap[color].border}"
>
    {#if recommended}
        <div class="recommended-badge">✨ Recomendado</div>
    {/if}
    
    {#if active}
        <div class="active-badge">✓ Activo</div>
    {/if}
    
    <div class="profile-header">
        <span class="profile-icon">{icon}</span>
        <h3 class="profile-name">{name}</h3>
    </div>
    
    {#if description}
        <p class="profile-description">{description}</p>
    {/if}
    
    {#if features.length > 0}
        <ul class="profile-features">
            {#each features as feature}
                {@const info = getFeatureInfo(feature)}
                {@const hasInfoData = info !== null}
                <li 
                    class="feature-item"
                    class:has-info={hasInfoData}
                    on:mouseenter={() => hasInfoData && showTooltip(feature)}
                    on:mouseleave={hideTooltip}
                    role="listitem"
                >
                    <span class="feature-check">{hasInfoData ? impactIcons[info.impact] : '✓'}</span>
                    <span class="feature-text">{feature}</span>
                    
                    {#if hasInfoData}
                        <button 
                            class="help-btn" 
                            on:click|stopPropagation={() => toggleTooltip(feature)}
                            title="Más información"
                        >
                            ?
                        </button>
                    {/if}
                    
                    {#if activeTooltip === feature && hasInfoData && info}
                        <div class="feature-tooltip" class:compact>
                            <div class="tooltip-header">
                                <strong>{info.name}</strong>
                            </div>
                            <p class="tooltip-casual">{info.casual}</p>
                            {#if !compact}
                                <p class="tooltip-technical">
                                    <span class="tech-label">Técnico:</span> {info.technical}
                                </p>
                            {/if}
                        </div>
                    {/if}
                </li>
            {/each}
        </ul>
    {/if}
    
    <button 
        class="profile-button"
        class:loading
        on:click={onApply}
        disabled={loading || disabled || active}
    >
        {#if loading}
            <span class="spinner-small"></span>
            {compact ? '...' : 'Aplicando...'}
        {:else if active}
            {compact ? '✓' : '✓ Aplicado'}
        {:else}
            {compact ? 'Aplicar' : 'Aplicar Perfil'}
        {/if}
    </button>
</div>

<style>
    .profile-card {
        background: var(--bg-elevated, #333);
        border-radius: 12px;
        padding: 1.25rem;
        position: relative;
        border: 2px solid transparent;
        transition: all 0.2s ease;
        overflow: visible;
    }
    
    .profile-card.compact {
        padding: 0.875rem;
    }
    
    .profile-card:hover {
        border-color: var(--accent-border);
        transform: translateY(-2px);
    }
    
    .profile-card.recommended {
        border-color: var(--primary, #00d4aa);
        background: var(--accent-bg);
    }
    
    .profile-card.active {
        border-color: var(--accent-border);
        background: var(--accent-bg);
        box-shadow: 0 0 15px rgba(0, 212, 170, 0.15);
    }
    
    .recommended-badge {
        position: absolute;
        top: -10px;
        right: 1rem;
        background: var(--primary, #00d4aa);
        color: #000;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .active-badge {
        position: absolute;
        top: -10px;
        left: 1rem;
        background: var(--accent-border);
        color: #000;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    
    .compact .recommended-badge,
    .compact .active-badge {
        font-size: 0.6rem;
        padding: 0.15rem 0.4rem;
        top: -8px;
    }
    
    .profile-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .profile-icon {
        font-size: 1.5rem;
    }
    
    .compact .profile-icon {
        font-size: 1.25rem;
    }
    
    .profile-name {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0;
    }
    
    .compact .profile-name {
        font-size: 0.9375rem;
    }
    
    .profile-description {
        font-size: 0.8rem;
        color: var(--text-secondary, #a0a0a0);
        margin: 0.5rem 0;
        line-height: 1.5;
    }
    
    .compact .profile-description {
        font-size: 0.6875rem;
        margin: 0.35rem 0;
    }
    
    .profile-features {
        list-style: none;
        padding: 0;
        margin: 0.75rem 0;
        overflow: visible;
    }
    
    .compact .profile-features {
        margin: 0.5rem 0;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: var(--text-muted, #888);
        padding: 0.25rem 0;
        position: relative;
        cursor: default;
        transition: color 0.15s;
    }
    
    .feature-item.has-info {
        cursor: help;
    }
    
    .feature-item:hover {
        color: var(--text-primary, #fff);
    }
    
    .feature-item.has-info:hover .help-btn {
        opacity: 1;
    }
    
    .help-btn {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 1px solid var(--border, #3d3d3d);
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-muted, #666);
        font-size: 0.625rem;
        font-weight: 700;
        cursor: pointer;
        opacity: 0.5;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-left: auto;
        flex-shrink: 0;
    }
    
    .help-btn:hover {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
        opacity: 1;
    }
    
    .compact .help-btn {
        width: 14px;
        height: 14px;
        font-size: 0.5rem;
    }
    
    .compact .feature-item {
        font-size: 0.6875rem;
        padding: 0.15rem 0;
        gap: 0.35rem;
    }
    
    .feature-check {
        font-size: 0.875rem;
        flex-shrink: 0;
    }
    
    .compact .feature-check {
        font-size: 0.75rem;
    }
    
    .feature-text {
        flex: 1;
    }
    
    /* Feature Tooltip */
    .feature-tooltip {
        position: absolute;
        bottom: calc(100% + 8px);
        left: 0;
        z-index: 9999;
        min-width: 220px;
        max-width: 280px;
        padding: 0.75rem;
        background: var(--bg-card, #1a1a1a);
        border: 1px solid var(--primary, #00d4aa);
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,212,170,0.2);
        pointer-events: none;
        animation: tooltipFadeIn 0.15s ease-out;
    }
    
    .feature-tooltip.compact {
        min-width: 180px;
        max-width: 240px;
        padding: 0.6rem;
    }
    
    @keyframes tooltipFadeIn {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .feature-tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 1rem;
        border: 6px solid transparent;
        border-top-color: var(--border, #3d3d3d);
    }
    
    .tooltip-header {
        margin-bottom: 0.5rem;
    }
    
    .tooltip-header strong {
        color: var(--primary, #00d4aa);
        font-size: 0.8125rem;
    }
    
    .tooltip-casual {
        font-size: 0.8125rem;
        color: var(--text-primary, #fff);
        margin: 0 0 0.5rem 0;
        line-height: 1.4;
    }
    
    .tooltip-technical {
        font-size: 0.6875rem;
        color: var(--text-muted, #666);
        margin: 0;
        line-height: 1.4;
        padding-top: 0.5rem;
        border-top: 1px solid var(--border, #3d3d3d);
    }
    
    .tech-label {
        color: var(--text-secondary, #a0a0a0);
        font-weight: 600;
    }
    
    .profile-button {
        width: 100%;
        padding: 0.75rem 1rem;
        margin-top: 1rem;
        background: var(--accent-border);
        color: #000;
        border: none;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .compact .profile-button {
        padding: 0.5rem 0.75rem;
        margin-top: 0.75rem;
        font-size: 0.75rem;
        border-radius: 6px;
    }
    
    .profile-button:hover:not(:disabled) {
        filter: brightness(1.1);
        transform: translateY(-1px);
    }
    
    .profile-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .profile-card.active .profile-button {
        background: rgba(255, 255, 255, 0.2);
        color: var(--text-primary, #fff);
    }
    
    .profile-button.loading {
        background: var(--bg-card, #2b2b2b);
        color: var(--text-secondary, #a0a0a0);
    }
    
    .spinner-small {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: var(--text-primary, #fff);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .compact .spinner-small {
        width: 12px;
        height: 12px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
