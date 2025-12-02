<!--
    Icon.svelte - Sistema de iconos SVG monocromáticos estilo industrial
    Basado en Lucide/Feather icons style
    By LOUST
-->
<script lang="ts">
    export let name: string;
    export let size: number = 20;
    export let strokeWidth: number = 1.5;
    export let className: string = '';
    
    // Los paths de iconos (stroke-based, estilo Lucide)
    const icons: Record<string, string> = {
        // Dashboard / Home
        'dashboard': 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
        'home': 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z M9 22V12h6v10',
        
        // Network / DNS
        'globe': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M2 12h20 M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z',
        'network': 'M5 12h14 M12 5v14 M18.5 5.5l-13 13 M5.5 5.5l13 13',
        'wifi': 'M5 12.55a11 11 0 0 1 14.08 0 M1.42 9a16 16 0 0 1 21.16 0 M8.53 16.11a6 6 0 0 1 6.95 0 M12 20h.01',
        'server': 'M2 5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5z M2 15a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4z M6 7h.01 M6 17h.01',
        
        // Optimization / Performance
        'zap': 'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
        'gauge': 'M12 16v-4 M12 12l4 2 M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z',
        'cpu': 'M4 4h16v16H4z M9 1v3 M15 1v3 M9 20v3 M15 20v3 M1 9h3 M1 15h3 M20 9h3 M20 15h3 M9 9h6v6H9z',
        'activity': 'M22 12h-4l-3 9L9 3l-3 9H2',
        
        // Monitor / Charts
        'chart-line': 'M3 3v18h18 M18 9l-5 5-4-4-6 6',
        'bar-chart': 'M12 20V10 M18 20V4 M6 20v-4',
        'trending-up': 'M23 6l-9.5 9.5-5-5L1 18 M17 6h6v6',
        'pulse': 'M22 12h-4l-3 9L9 3l-3 9H2',
        
        // Alerts / Notifications
        'bell': 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9 M13.73 21a2 2 0 0 1-3.46 0',
        'bell-ring': 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9 M13.73 21a2 2 0 0 1-3.46 0 M2 8c0-1.1.2-2.1.5-3 M22 8c0-1.1-.2-2.1-.5-3',
        'alert-triangle': 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z M12 9v4 M12 17h.01',
        'alert-circle': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 8v4 M12 16h.01',
        
        // Settings / Config
        'settings': 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z',
        'sliders': 'M4 21v-7 M4 10V3 M12 21v-9 M12 8V3 M20 21v-5 M20 12V3 M1 14h6 M9 8h6 M17 16h6',
        
        // Documentation / Info
        'book-open': 'M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z',
        'file-text': 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8',
        'info': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 16v-4 M12 8h.01',
        
        // GitHub / Code
        'github': 'M9 19c-5 1.5-5-2.5-7-3 M14 22v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 18 4.77 5.07 5.07 0 0 0 17.91 1S16.73.65 14 2.48a13.38 13.38 0 0 0-7 0C4.27.65 3.09 1 3.09 1A5.07 5.07 0 0 0 3 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 7 18.13V22',
        'code': 'M16 18l6-6-6-6 M8 6l-6 6 6 6',
        'git-branch': 'M6 3v12 M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M18 9a9 9 0 0 1-9 9',
        
        // Actions
        'play': 'M5 3l14 9-14 9V3z',
        'pause': 'M6 4h4v16H6z M14 4h4v16h-4z',
        'stop': 'M6 4h12v16H6z',
        'refresh': 'M23 4v6h-6 M1 20v-6h6 M3.51 9a9 9 0 0 1 14.85-3.36L23 10 M1 14l4.64 4.36A9 9 0 0 0 20.49 15',
        'download': 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M7 10l5 5 5-5 M12 15V3',
        'upload': 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4 M17 8l-5-5-5 5 M12 3v12',
        
        // Navigation
        'chevron-left': 'M15 18l-6-6 6-6',
        'chevron-right': 'M9 18l6-6-6-6',
        'chevron-up': 'M18 15l-6-6-6 6',
        'chevron-down': 'M6 9l6 6 6-6',
        'menu': 'M3 12h18 M3 6h18 M3 18h18',
        'x': 'M18 6L6 18 M6 6l12 12',
        
        // Status
        'check': 'M20 6L9 17l-5-5',
        'check-circle': 'M22 11.08V12a10 10 0 1 1-5.93-9.14 M22 4L12 14.01l-3-3',
        'x-circle': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M15 9l-6 6 M9 9l6 6',
        'loader': 'M12 2v4 M12 18v4 M4.93 4.93l2.83 2.83 M16.24 16.24l2.83 2.83 M2 12h4 M18 12h4 M4.93 19.07l2.83-2.83 M16.24 7.76l2.83-2.83',
        
        // Network specific
        'signal': 'M2 20h.01 M7 20v-4 M12 20v-8 M17 20V8 M22 20V4',
        'router': 'M2 16V6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2z M12 18v4 M6 22h12 M6 10h.01 M10 10h.01',
        'shield': 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
        'lock': 'M19 11H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2z M7 11V7a5 5 0 0 1 10 0v4',
        
        // Terminal
        'terminal': 'M4 17l6-6-6-6 M12 19h8',
        'command': 'M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0 3-3 3 3 0 0 0-3-3z',
        
        // Misc
        'clock': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 6v6l4 2',
        'eye': 'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6z',
        'target': 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 6a6 6 0 1 0 0 12 6 6 0 0 0 0-12z M12 10a2 2 0 1 0 0 4 2 2 0 0 0 0-4z',
        'layers': 'M12 2L2 7l10 5 10-5-10-5z M2 17l10 5 10-5 M2 12l10 5 10-5',
    };
    
    $: path = icons[name] || icons['x'];
</script>

<svg 
    class="icon {className}"
    width={size} 
    height={size} 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    stroke-width={strokeWidth}
    stroke-linecap="round" 
    stroke-linejoin="round"
>
    {#each path.split(' M').map((p, i) => i === 0 ? p : 'M' + p) as segment}
        <path d={segment} />
    {/each}
</svg>

<style>
    .icon {
        display: inline-block;
        vertical-align: middle;
        flex-shrink: 0;
    }
</style>
