<script lang="ts">
    /**
     * Animated Logo Component
     * Logo con efecto typing y transformación Matrix CONSISTENTE
     * - Mismo color durante toda la animación y después
     * - Mismo tamaño de fuente en todos los estados
     */
    import { onMount, onDestroy } from 'svelte';
    
    export let collapsed = false;
    
    // Estados del logo
    type LogoState = 'typing' | 'display' | 'transform';
    
    let logoState: LogoState = 'typing';
    let displayText = '';
    let currentWord: 'netboozt' | 'opensource' = 'netboozt';
    let intervalId: ReturnType<typeof setInterval> | null = null;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    
    const NETBOOZT = 'NetBoozt';
    const OPENSOURCE = 'OpenSource';
    const TYPING_SPEED = 120;
    const TRANSFORM_SPEED = 80;
    const DISPLAY_DURATION = 12000; // 12 segundos
    
    // Caracteres para efecto matrix - solo caracteres simples
    const MATRIX_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    
    onMount(() => {
        startTypingAnimation();
    });
    
    onDestroy(() => {
        cleanup();
    });
    
    function cleanup() {
        if (intervalId) clearInterval(intervalId);
        if (timeoutId) clearTimeout(timeoutId);
    }
    
    function startTypingAnimation() {
        cleanup();
        let charIndex = 0;
        displayText = '';
        logoState = 'typing';
        currentWord = 'netboozt';
        
        intervalId = setInterval(() => {
            if (charIndex < NETBOOZT.length) {
                displayText = NETBOOZT.substring(0, charIndex + 1);
                charIndex++;
            } else {
                if (intervalId) clearInterval(intervalId);
                logoState = 'display';
                
                timeoutId = setTimeout(() => {
                    transformTo('opensource');
                }, DISPLAY_DURATION);
            }
        }, TYPING_SPEED);
    }
    
    function transformTo(target: 'netboozt' | 'opensource') {
        cleanup();
        logoState = 'transform';
        
        const targetText = target === 'opensource' ? OPENSOURCE : NETBOOZT;
        const maxLen = Math.max(displayText.length, targetText.length);
        let iterations = 0;
        const maxIterations = maxLen + 5;
        
        intervalId = setInterval(() => {
            let result = '';
            for (let i = 0; i < targetText.length; i++) {
                if (iterations > i + 3) {
                    // Caracter ya revelado
                    result += targetText[i];
                } else {
                    // Caracter en transición matrix
                    result += MATRIX_CHARS[Math.floor(Math.random() * MATRIX_CHARS.length)];
                }
            }
            displayText = result;
            iterations++;
            
            if (iterations > maxIterations) {
                if (intervalId) clearInterval(intervalId);
                displayText = targetText;
                currentWord = target;
                logoState = 'display';
                
                // Programar siguiente transición
                const nextTarget = target === 'opensource' ? 'netboozt' : 'opensource';
                timeoutId = setTimeout(() => {
                    transformTo(nextTarget);
                }, DISPLAY_DURATION);
            }
        }, TRANSFORM_SPEED);
    }
</script>

<div class="animated-logo" class:collapsed>
    <span class="logo-text" class:transforming={logoState === 'transform'}>
        {displayText}
        {#if logoState === 'typing'}
            <span class="cursor">|</span>
        {/if}
    </span>
</div>

<style>
    .animated-logo {
        display: flex;
        align-items: center;
        overflow: hidden;
    }
    
    .animated-logo.collapsed {
        display: none;
    }
    
    .logo-text {
        font-size: 1.125rem;
        font-weight: 700;
        color: #ffffff;
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        letter-spacing: 0.5px;
        white-space: nowrap;
        /* Mantener tamaño fijo para evitar saltos */
        min-width: 7ch;
    }
    
    .logo-text.transforming {
        /* Sin efectos - mantener consistencia */
        opacity: 1;
    }
    
    .cursor {
        animation: blink 0.8s infinite step-end;
        color: #00d4aa;
        font-weight: 400;
        display: none; /* Ocultar cursor/separador */
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
</style>
