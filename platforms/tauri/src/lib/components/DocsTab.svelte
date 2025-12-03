<script lang="ts">
    /**
     * Documentation Tab Component
     * Documentación de uso integrada con navegación por anclas
     */
    import { onMount } from 'svelte';
    
    let contentContainer: HTMLElement;
    let activeSection = 'quickstart';
    
    const sections = [
        { id: 'readme', name: 'README', icon: '📄' },
        { id: 'quickstart', name: 'Inicio Rápido', icon: '🚀' },
        { id: 'dns', name: 'DNS', icon: '🌐' },
        { id: 'optimize', name: 'Optimizaciones', icon: '⚡' },
        { id: 'dryrun', name: 'Modo Dry-Run', icon: '🧪' },
        { id: 'troubleshoot', name: 'Solución de Problemas', icon: '🔧' },
        { id: 'glossary', name: 'Glosario', icon: '📖' }
    ];
    
    let readmeContent = '';
    let readmeLoading = true;
    let readmeError = '';
    
    async function fetchReadme() {
        try {
            const res = await fetch('https://raw.githubusercontent.com/louzt/NetBoozt_InternetUpgrade/main/README.md');
            if (!res.ok) throw new Error('No se pudo cargar');
            readmeContent = await res.text();
        } catch (e) {
            readmeError = 'No se pudo cargar el README. Verifica tu conexión.';
        } finally {
            readmeLoading = false;
        }
    }
    
    function scrollToSection(sectionId: string) {
        const element = document.getElementById(`doc-${sectionId}`);
        if (element && contentContainer) {
            const containerTop = contentContainer.getBoundingClientRect().top;
            const elementTop = element.getBoundingClientRect().top;
            const offset = elementTop - containerTop + contentContainer.scrollTop - 20;
            
            contentContainer.scrollTo({
                top: offset,
                behavior: 'smooth'
            });
            activeSection = sectionId;
        }
    }
    
    function handleScroll() {
        if (!contentContainer) return;
        
        const containerTop = contentContainer.getBoundingClientRect().top;
        const scrollPosition = contentContainer.scrollTop + 100; // offset for header
        
        for (let i = sections.length - 1; i >= 0; i--) {
            const element = document.getElementById(`doc-${sections[i].id}`);
            if (element) {
                const elementTop = element.offsetTop;
                if (scrollPosition >= elementTop) {
                    activeSection = sections[i].id;
                    break;
                }
            }
        }
    }
    
    onMount(() => {
        fetchReadme();
        if (contentContainer) {
            contentContainer.addEventListener('scroll', handleScroll);
            return () => contentContainer.removeEventListener('scroll', handleScroll);
        }
    });
</script>

<div class="docs-page">
    <nav class="docs-nav">
        <div class="nav-header">
            <span class="nav-title">Documentación</span>
        </div>
        <div class="nav-items">
            {#each sections as section}
                <button 
                    class="docs-nav-item" 
                    class:active={activeSection === section.id}
                    on:click={() => scrollToSection(section.id)}
                >
                    <span class="nav-icon">{section.icon}</span>
                    <span class="nav-text">{section.name}</span>
                    <span class="nav-indicator"></span>
                </button>
            {/each}
        </div>
        <div class="nav-footer">
            <span class="scroll-hint">↓ Scroll para navegar</span>
        </div>
    </nav>
    
    <div class="docs-content" bind:this={contentContainer}>
        <!-- README from GitHub -->
        <article class="doc-article" id="doc-readme">
            <h1>📄 README de GitHub</h1>
            
            <section class="doc-section">
                <div class="readme-actions">
                    <a href="https://github.com/louzt/NetBoozt_InternetUpgrade" target="_blank" class="btn-readme">
                        <span>🔗</span> Ver en GitHub
                    </a>
                    <a href="https://github.com/louzt/NetBoozt_InternetUpgrade/releases" target="_blank" class="btn-readme">
                        <span>📦</span> Releases
                    </a>
                </div>
                
                {#if readmeLoading}
                    <div class="readme-loading">
                        <div class="spinner"></div>
                        <span>Cargando README...</span>
                    </div>
                {:else if readmeError}
                    <div class="readme-error">
                        <span>⚠️</span>
                        <p>{readmeError}</p>
                        <button class="btn-retry" on:click={fetchReadme}>Reintentar</button>
                    </div>
                {:else}
                    <div class="readme-content">
                        <pre class="readme-raw">{readmeContent}</pre>
                    </div>
                {/if}
            </section>
        </article>
        
        <!-- Quickstart -->
        <article class="doc-article" id="doc-quickstart">
            <h1>🚀 Inicio Rápido</h1>
            
            <section class="doc-section">
                <h2>¿Qué es NetBoozt?</h2>
                <p>NetBoozt es una herramienta de optimización de red para Windows que mejora tu conexión a internet mediante:</p>
                <ul>
                    <li><strong>Optimización DNS</strong> - Usa los servidores DNS más rápidos</li>
                    <li><strong>Configuración TCP/IP</strong> - Ajusta parámetros de red para mejor rendimiento</li>
                    <li><strong>Monitoreo en tiempo real</strong> - Visualiza métricas de tu conexión</li>
                    <li><strong>Diagnóstico automático</strong> - Detecta problemas de conectividad</li>
                </ul>
            </section>
            
            <section class="doc-section">
                <h2>Pasos básicos</h2>
                <div class="steps">
                    <div class="step">
                        <span class="step-number">1</span>
                        <div class="step-content">
                            <h3>Ejecuta el diagnóstico</h3>
                            <p>Ve al Dashboard y haz clic en "Ejecutar Diagnóstico de 4 Fases" para verificar el estado de tu conexión.</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">2</span>
                        <div class="step-content">
                            <h3>Cambia tu DNS</h3>
                            <p>En la pestaña DNS, selecciona un servidor rápido como Cloudflare o Google para mejorar la resolución de nombres.</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">3</span>
                        <div class="step-content">
                            <h3>Aplica optimizaciones</h3>
                            <p>En Optimizar, selecciona un perfil según tu nivel de experiencia. Recomendamos "Balanceado" para la mayoría.</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">4</span>
                        <div class="step-content">
                            <h3>Monitorea los resultados</h3>
                            <p>Usa el Monitor en tiempo real para ver cómo han mejorado tus métricas de red.</p>
                        </div>
                    </div>
                </div>
            </section>
        </article>
        
        <!-- DNS -->
        <article class="doc-article" id="doc-dns">
            <h1>🌐 Configuración DNS</h1>
            
            <section class="doc-section">
                <h2>¿Qué es DNS?</h2>
                <p>DNS (Domain Name System) traduce nombres de dominio como "google.com" a direcciones IP. Un DNS lento significa navegación lenta.</p>
            </section>
            
            <section class="doc-section">
                <h2>Servidores DNS disponibles</h2>
                <table class="doc-table">
                    <thead>
                        <tr>
                            <th>Proveedor</th>
                            <th>IP Principal</th>
                            <th>Características</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Cloudflare</td><td>1.1.1.1</td><td>🚀 El más rápido, privacidad</td></tr>
                        <tr><td>Google</td><td>8.8.8.8</td><td>🌍 Más confiable, global</td></tr>
                        <tr><td>Quad9</td><td>9.9.9.9</td><td>🛡️ Bloquea malware</td></tr>
                        <tr><td>OpenDNS</td><td>208.67.222.222</td><td>👨‍👩‍👧 Control parental</td></tr>
                        <tr><td>AdGuard</td><td>94.140.14.14</td><td>🚫 Bloquea anuncios</td></tr>
                    </tbody>
                </table>
            </section>
            
            <section class="doc-section">
                <h2>Auto-Failover</h2>
                <p>Cuando está activado, NetBoozt cambiará automáticamente a otro servidor DNS si detecta que el actual no responde. Esto asegura que siempre tengas conectividad.</p>
                <div class="info-box">
                    <span class="info-icon">💡</span>
                    <p>El sistema usa 8 niveles (tiers) de DNS, desde el más rápido hasta el DNS de tu ISP como último recurso.</p>
                </div>
            </section>
        </article>
        
        <!-- Optimizations -->
        <article class="doc-article" id="doc-optimize">
            <h1>⚡ Optimizaciones TCP/IP</h1>
            
            <section class="doc-section">
                <h2>Perfiles de Optimización</h2>
                <div class="profile-docs">
                    <div class="profile-doc conservative">
                        <h3>🟢 Conservador</h3>
                        <p>Cambios seguros que no deberían causar problemas:</p>
                        <ul>
                            <li><strong>RSS</strong> - Distribuye paquetes entre CPUs</li>
                            <li><strong>RSC</strong> - Combina segmentos TCP</li>
                            <li><strong>Autotuning</strong> - Buffers dinámicos</li>
                        </ul>
                    </div>
                    <div class="profile-doc balanced">
                        <h3>🟡 Balanceado</h3>
                        <p>Mejor rendimiento con bajo riesgo:</p>
                        <ul>
                            <li>Todo lo del Conservador</li>
                            <li><strong>ECN</strong> - Detecta congestión sin pérdidas</li>
                            <li><strong>HyStart++</strong> - Inicio rápido mejorado</li>
                            <li><strong>PRR</strong> - Recuperación proporcional</li>
                        </ul>
                    </div>
                    <div class="profile-doc aggressive">
                        <h3>🔴 Agresivo</h3>
                        <p>Máximo rendimiento para usuarios avanzados:</p>
                        <ul>
                            <li>Todo lo del Balanceado</li>
                            <li><strong>TCP Fast Open</strong> - Ahorra 1 RTT</li>
                            <li><strong>TCP Pacing</strong> - Envío suave</li>
                            <li><strong>Initial RTO</strong> - Timeout reducido</li>
                        </ul>
                    </div>
                </div>
            </section>
            
            <section class="doc-section">
                <h2>🔬 Detalles Técnicos de Cada Optimización</h2>
                
                <div class="tech-detail">
                    <h3>🚀 RSS (Receive Side Scaling)</h3>
                    <div class="detail-content">
                        <p class="casual">Usa todos los núcleos de tu CPU para procesar datos de red más rápido, evitando cuellos de botella.</p>
                        <p class="technical"><strong>Técnico:</strong> Distribuye el procesamiento de paquetes entrantes entre múltiples CPUs usando hashing de conexiones (IP + Puerto). Esencial para conexiones de alta velocidad (&gt;1Gbps).</p>
                        <span class="impact-badge speed">🚀 Velocidad</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>🚀 RSC (Receive Segment Coalescing)</h3>
                    <div class="detail-content">
                        <p class="casual">Agrupa paquetes pequeños en uno grande para menos trabajo del CPU.</p>
                        <p class="technical"><strong>Técnico:</strong> Combina múltiples segmentos TCP en uno solo, reduciendo el número de interrupciones de CPU y el overhead de procesamiento de headers.</p>
                        <span class="impact-badge speed">🚀 Velocidad</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>🚀 Autotuning (Window Auto-Tuning)</h3>
                    <div class="detail-content">
                        <p class="casual">Ajusta automáticamente el tamaño del buffer para mejor velocidad según tu conexión.</p>
                        <p class="technical"><strong>Técnico:</strong> Ajusta dinámicamente la ventana de recepción TCP hasta 16MB según RTT y ancho de banda. El nivel "experimental" permite valores aún mayores para conexiones muy rápidas.</p>
                        <span class="impact-badge speed">🚀 Velocidad</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>🛡️ ECN (Explicit Congestion Notification)</h3>
                    <div class="detail-content">
                        <p class="casual">Detecta congestión en la red ANTES de perder paquetes, manteniendo la conexión estable.</p>
                        <p class="technical"><strong>Técnico:</strong> RFC 3168: Los routers pueden señalar congestión marcando bits en el header IP en lugar de descartar paquetes. Reduce retransmisiones y mejora latencia bajo carga.</p>
                        <span class="impact-badge stability">🛡️ Estabilidad</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>⚡ HyStart++ (Hybrid Slow Start)</h3>
                    <div class="detail-content">
                        <p class="casual">Acelera más inteligente al inicio de la conexión sin saturar tu red.</p>
                        <p class="technical"><strong>Técnico:</strong> Sale del slow-start antes de causar pérdidas de paquetes, detectando el punto de inflexión del delay. Similar al comportamiento de BBR de Google.</p>
                        <span class="impact-badge latency">⚡ Latencia</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>🛡️ PRR (Proportional Rate Reduction)</h3>
                    <div class="detail-content">
                        <p class="casual">Se recupera más suave después de problemas de red, sin fluctuaciones bruscas.</p>
                        <p class="technical"><strong>Técnico:</strong> RFC 6937: Recuperación gradual de pérdidas en lugar de reducir la ventana al 50% como hacía el algoritmo Reno clásico.</p>
                        <span class="impact-badge stability">🛡️ Estabilidad</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>⚡ TCP Fast Open (TFO)</h3>
                    <div class="detail-content">
                        <p class="casual">Envía datos más rápido al conectar, ahorrando tiempo en cada nueva conexión.</p>
                        <p class="technical"><strong>Técnico:</strong> RFC 7413: Permite enviar datos en el paquete SYN del handshake TCP, ahorrando 1 RTT completo en conexiones repetidas usando cookies.</p>
                        <span class="impact-badge latency">⚡ Latencia</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>⚡ TCP Pacing</h3>
                    <div class="detail-content">
                        <p class="casual">Envía datos de forma uniforme, evita atascos y hace la conexión más fluida.</p>
                        <p class="technical"><strong>Técnico:</strong> Distribuye los paquetes uniformemente en el tiempo en lugar de enviarlos en ráfagas. Técnica clave del algoritmo BBR que reduce significativamente el bufferbloat.</p>
                        <span class="impact-badge latency">⚡ Latencia</span>
                    </div>
                </div>
                
                <div class="tech-detail">
                    <h3>⚡ Initial RTO Reducido</h3>
                    <div class="detail-content">
                        <p class="casual">Detecta problemas más rápido cuando algo falla (1 segundo vs 3 por defecto).</p>
                        <p class="technical"><strong>Técnico:</strong> Reduce el Initial Retransmission Timeout de 3000ms (default) a 1000ms. Detecta pérdidas más rápido, mejorando latencia en redes inestables.</p>
                        <span class="impact-badge latency">⚡ Latencia</span>
                    </div>
                </div>
            </section>
            
            <section class="doc-section">
                <h2>📊 CUBIC vs BBR</h2>
                <p>Windows usa <strong>CUBIC</strong> como algoritmo de control de congestión por defecto. Linux tiene <strong>BBR</strong> desarrollado por Google.</p>
                
                <div class="comparison-table">
                    <div class="comparison-item">
                        <h4>CUBIC (Windows)</h4>
                        <ul>
                            <li>Reduce velocidad 50% ante pérdidas</li>
                            <li>Recuperación lenta (función cúbica)</li>
                            <li>Sensible a pérdidas de paquetes</li>
                        </ul>
                    </div>
                    <div class="comparison-item bbr">
                        <h4>BBR-like (Con optimizaciones)</h4>
                        <ul>
                            <li>Mantiene velocidad estable</li>
                            <li>Mide ancho de banda real</li>
                            <li>Tolera pérdidas aisladas</li>
                        </ul>
                    </div>
                </div>
                
                <div class="info-box">
                    <span class="info-icon">💡</span>
                    <p>Las optimizaciones de NetBoozt (HyStart++, PRR, Pacing, ECN) aplican los principios de BBR sobre CUBIC, logrando un comportamiento más eficiente sin cambiar el algoritmo base.</p>
                </div>
            </section>
            
            <section class="doc-section">
                <h2>⚠️ Advertencias</h2>
                <div class="warning-box">
                    <span class="warning-icon">⚠️</span>
                    <div>
                        <p><strong>Algunos cambios requieren reinicio</strong> del sistema para aplicarse completamente.</p>
                        <p>Si experimentas problemas, usa "Restaurar valores por defecto" para volver a la configuración original.</p>
                    </div>
                </div>
            </section>
        </article>
        
        <!-- Dry-Run -->
        <article class="doc-article" id="doc-dryrun">
            <h1>🧪 Modo Dry-Run</h1>
            
            <section class="doc-section">
                <h2>¿Qué es el Modo Dry-Run?</h2>
                <p>El modo Dry-Run (ejecución en seco) te permite <strong>previsualizar los cambios</strong> que se harían sin aplicarlos realmente al sistema.</p>
                
                <div class="info-box">
                    <span class="info-icon">💡</span>
                    <p>Es como un "modo seguro" que te muestra exactamente qué comandos se ejecutarían y qué valores cambiarían.</p>
                </div>
            </section>
            
            <section class="doc-section">
                <h2>¿Para qué sirve?</h2>
                <ul>
                    <li>🔍 <strong>Aprender</strong> - Entiende qué hace cada optimización</li>
                    <li>✅ <strong>Verificar</strong> - Revisa los cambios antes de aplicarlos</li>
                    <li>📋 <strong>Documentar</strong> - Guarda un log de lo que se cambiaría</li>
                    <li>🧪 <strong>Probar</strong> - Experimenta sin riesgo</li>
                </ul>
            </section>
            
            <section class="doc-section">
                <h2>Cómo usarlo</h2>
                <div class="code-block">
                    <span class="code-title">Ejemplo de salida Dry-Run:</span>
                    <pre>
[DRY-RUN] Cambios que se aplicarían:

1. DNS
   Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" 
   -ServerAddresses 1.1.1.1,1.0.0.1

2. TCP Autotuning
   netsh int tcp set global autotuninglevel=normal
   Valor actual: restricted → Nuevo: normal

3. ECN
   netsh int tcp set global ecncapability=enabled
   Valor actual: disabled → Nuevo: enabled
                    </pre>
                </div>
            </section>
        </article>
        
        <!-- Troubleshoot -->
        <article class="doc-article" id="doc-troubleshoot">
            <h1>🔧 Solución de Problemas</h1>
            
            <section class="doc-section">
                <h2>Problemas comunes</h2>
                
                <div class="faq-item">
                    <h3>❓ No puedo cambiar el DNS</h3>
                    <p>Asegúrate de ejecutar NetBoozt como <strong>Administrador</strong>. Haz clic derecho en el icono y selecciona "Ejecutar como administrador".</p>
                </div>
                
                <div class="faq-item">
                    <h3>❓ La conexión empeoró después de optimizar</h3>
                    <p>Ve a Optimizar → "Restaurar valores por defecto". Luego prueba con el perfil "Conservador" que es más seguro.</p>
                </div>
                
                <div class="faq-item">
                    <h3>❓ El diagnóstico falla en la fase DNS</h3>
                    <p>Tu servidor DNS actual puede estar caído. Usa la pestaña DNS para cambiar a Cloudflare (1.1.1.1) o Google (8.8.8.8).</p>
                </div>
                
                <div class="faq-item">
                    <h3>❓ No veo ningún adaptador de red</h3>
                    <p>Verifica que tu adaptador de red esté habilitado en Panel de Control → Centro de redes. También prueba reiniciar el servicio de red.</p>
                </div>
            </section>
            
            <section class="doc-section">
                <h2>Comandos útiles (PowerShell)</h2>
                <div class="code-block">
                    <pre>
# Ver DNS actual
Get-DnsClientServerAddress

# Limpiar caché DNS
Clear-DnsClientCache

# Ver configuración TCP
netsh int tcp show global

# Resetear Winsock
netsh winsock reset
                    </pre>
                </div>
            </section>
        </article>
        
        <!-- Glossary -->
        <article class="doc-article" id="doc-glossary">
            <h1>📖 Glosario</h1>
            
            <section class="doc-section">
                <div class="glossary-grid">
                    <div class="glossary-item">
                        <h3>DNS</h3>
                        <p>Domain Name System. Traduce nombres de dominio a direcciones IP.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>TCP</h3>
                        <p>Transmission Control Protocol. Protocolo de transporte confiable.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>RSS</h3>
                        <p>Receive Side Scaling. Distribuye procesamiento de paquetes entre múltiples CPUs.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>RSC</h3>
                        <p>Receive Segment Coalescing. Combina múltiples segmentos TCP en uno.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>ECN</h3>
                        <p>Explicit Congestion Notification. Detecta congestión sin perder paquetes.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>RTT</h3>
                        <p>Round-Trip Time. Tiempo que tarda un paquete en ir y volver.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>Latencia</h3>
                        <p>Tiempo de respuesta de la red, medido en milisegundos (ms).</p>
                    </div>
                    <div class="glossary-item">
                        <h3>ISP</h3>
                        <p>Internet Service Provider. Tu proveedor de internet (ej: Telmex, Izzi).</p>
                    </div>
                    <div class="glossary-item">
                        <h3>Gateway</h3>
                        <p>Puerta de enlace. Normalmente es tu router/modem.</p>
                    </div>
                    <div class="glossary-item">
                        <h3>DHCP</h3>
                        <p>Dynamic Host Configuration Protocol. Asigna IPs automáticamente.</p>
                    </div>
                </div>
            </section>
        </article>
    </div>
</div>

<style>
    .docs-page {
        display: grid;
        grid-template-columns: 200px 1fr;
        gap: 1.5rem;
        height: 100%;
        max-height: 100%;
        overflow: hidden;
    }
    
    .docs-nav {
        display: flex;
        flex-direction: column;
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        height: fit-content;
        max-height: 100%;
        position: sticky;
        top: 0;
        overflow: hidden;
    }
    
    .nav-header {
        padding: 1rem 1rem 0.5rem;
        border-bottom: 1px solid var(--border, #2d2d2d);
    }
    
    .nav-title {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted, #666);
    }
    
    .nav-items {
        display: flex;
        flex-direction: column;
        gap: 0.125rem;
        padding: 0.5rem;
    }
    
    .docs-nav-item {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        padding: 0.625rem 0.75rem;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8125rem;
        cursor: pointer;
        transition: all 0.15s ease;
        text-align: left;
        position: relative;
    }
    
    .docs-nav-item:hover {
        background: var(--bg-elevated, #2b2b2b);
        color: var(--text-primary, #fff);
    }
    
    .docs-nav-item.active {
        background: rgba(0, 212, 170, 0.15);
        color: var(--primary, #00d4aa);
    }
    
    .docs-nav-item.active .nav-indicator {
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 60%;
        background: var(--primary, #00d4aa);
        border-radius: 0 2px 2px 0;
    }
    
    .nav-icon {
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    
    .nav-text {
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .nav-footer {
        padding: 0.75rem 1rem;
        border-top: 1px solid var(--border, #2d2d2d);
    }
    
    .scroll-hint {
        font-size: 0.6875rem;
        color: var(--text-muted, #555);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .docs-content {
        background: var(--bg-card, #1a1a1a);
        border-radius: 12px;
        padding: 2rem;
        overflow-y: auto;
        scroll-behavior: smooth;
    }
    
    .doc-article {
        margin-bottom: 4rem;
        scroll-margin-top: 2rem;
    }
    
    .doc-article:last-child {
        margin-bottom: 2rem;
    }
    
    .doc-article h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
        margin: 0 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border, #2d2d2d);
    }
    
    .doc-section {
        margin-bottom: 2rem;
    }
    
    .doc-section h2 {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--primary, #00d4aa);
        margin: 0 0 1rem 0;
    }
    
    .doc-section p {
        color: var(--text-secondary, #a0a0a0);
        line-height: 1.7;
        margin: 0 0 1rem 0;
    }
    
    .doc-section ul {
        color: var(--text-secondary, #a0a0a0);
        line-height: 1.7;
        padding-left: 1.5rem;
    }
    
    .doc-section li {
        margin-bottom: 0.5rem;
    }
    
    .steps {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .step {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
    }
    
    .step-number {
        width: 32px;
        height: 32px;
        background: var(--primary, #00d4aa);
        color: #000;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        flex-shrink: 0;
    }
    
    .step-content h3 {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        margin: 0 0 0.25rem 0;
    }
    
    .step-content p {
        margin: 0;
        font-size: 0.875rem;
    }
    
    .doc-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .doc-table th, .doc-table td {
        text-align: left;
        padding: 0.75rem;
        border-bottom: 1px solid var(--border, #2d2d2d);
    }
    
    .doc-table th {
        color: var(--text-muted, #666);
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    
    .doc-table td {
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.875rem;
    }
    
    .info-box, .warning-box {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.3);
    }
    
    .warning-box {
        background: rgba(253, 203, 110, 0.1);
        border: 1px solid rgba(253, 203, 110, 0.3);
    }
    
    .info-icon, .warning-icon {
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    
    .info-box p, .warning-box p {
        margin: 0;
        font-size: 0.875rem;
    }
    
    .profile-docs {
        display: grid;
        gap: 1rem;
    }
    
    .profile-doc {
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    .profile-doc.conservative {
        background: rgba(0, 212, 170, 0.05);
        border-left-color: #00d4aa;
    }
    
    .profile-doc.balanced {
        background: rgba(253, 203, 110, 0.05);
        border-left-color: #fdcb6e;
    }
    
    .profile-doc.aggressive {
        background: rgba(255, 107, 107, 0.05);
        border-left-color: #ff6b6b;
    }
    
    .profile-doc h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        color: var(--text-primary, #fff);
    }
    
    .profile-doc p {
        margin: 0 0 0.75rem 0;
        font-size: 0.875rem;
    }
    
    .profile-doc ul {
        margin: 0;
        padding-left: 1.25rem;
        font-size: 0.8125rem;
    }
    
    .code-block {
        background: #0d0d0d;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .code-title {
        display: block;
        padding: 0.75rem 1rem;
        background: #151515;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
        border-bottom: 1px solid var(--border, #2d2d2d);
    }
    
    .code-block pre {
        margin: 0;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8125rem;
        color: var(--primary, #00d4aa);
        overflow-x: auto;
        line-height: 1.6;
    }
    
    .faq-item {
        padding: 1rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
        margin-bottom: 0.75rem;
    }
    
    .faq-item h3 {
        font-size: 0.9375rem;
        color: var(--text-primary, #fff);
        margin: 0 0 0.5rem 0;
    }
    
    .faq-item p {
        margin: 0;
        font-size: 0.875rem;
    }
    
    .glossary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .glossary-item {
        padding: 1rem;
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
    }
    
    .glossary-item h3 {
        font-size: 0.9375rem;
        color: var(--primary, #00d4aa);
        margin: 0 0 0.5rem 0;
    }
    
    .glossary-item p {
        margin: 0;
        font-size: 0.8125rem;
    }
    
    /* Technical Details */
    .tech-detail {
        background: var(--bg-elevated, #2b2b2b);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid var(--primary, #00d4aa);
    }
    
    .tech-detail h3 {
        font-size: 0.9375rem;
        color: var(--text-primary, #fff);
        margin: 0 0 0.75rem 0;
    }
    
    .tech-detail .detail-content {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .tech-detail .casual {
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
        margin: 0;
        line-height: 1.5;
    }
    
    .tech-detail .technical {
        font-size: 0.75rem;
        color: var(--text-muted, #888);
        margin: 0;
        line-height: 1.5;
        padding: 0.5rem;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
    }
    
    .impact-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.6875rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        width: fit-content;
    }
    
    .impact-badge.speed {
        background: rgba(0, 212, 170, 0.15);
        color: #00d4aa;
    }
    
    .impact-badge.stability {
        background: rgba(253, 203, 110, 0.15);
        color: #fdcb6e;
    }
    
    .impact-badge.latency {
        background: rgba(130, 177, 255, 0.15);
        color: #82b1ff;
    }
    
    /* Comparison Table */
    .comparison-table {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .comparison-item {
        padding: 1rem;
        background: rgba(255, 193, 7, 0.05);
        border: 1px solid rgba(255, 193, 7, 0.2);
        border-radius: 10px;
    }
    
    .comparison-item.bbr {
        background: rgba(0, 212, 170, 0.05);
        border-color: rgba(0, 212, 170, 0.2);
    }
    
    .comparison-item h4 {
        font-size: 0.875rem;
        color: var(--text-primary, #fff);
        margin: 0 0 0.75rem 0;
    }
    
    .comparison-item ul {
        margin: 0;
        padding-left: 1.25rem;
        font-size: 0.8125rem;
    }
    
    @media (max-width: 768px) {
        .comparison-table {
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 768px) {
        .docs-page {
            grid-template-columns: 1fr;
        }
        
        .docs-nav {
            flex-direction: row;
            overflow-x: auto;
            position: static;
        }
        
        .nav-header, .nav-footer {
            display: none;
        }
        
        .nav-items {
            flex-direction: row;
            padding: 0.5rem;
        }
        
        .nav-text {
            display: none;
        }
        
        .docs-nav-item {
            padding: 0.5rem 0.75rem;
        }
    }
    
    /* README Section */
    .readme-actions {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .btn-readme {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8125rem;
        text-decoration: none;
        transition: all 0.15s ease;
    }
    
    .btn-readme:hover {
        background: var(--primary, #00d4aa);
        color: #000;
        border-color: var(--primary, #00d4aa);
    }
    
    .readme-loading {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 2rem;
        color: var(--text-muted, #666);
    }
    
    .readme-loading .spinner {
        width: 24px;
        height: 24px;
        border: 2px solid var(--border, #3d3d3d);
        border-top-color: var(--primary, #00d4aa);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .readme-error {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 2rem;
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 10px;
        text-align: center;
    }
    
    .readme-error span {
        font-size: 2rem;
    }
    
    .readme-error p {
        color: var(--text-secondary, #a0a0a0);
        margin: 0;
    }
    
    .btn-retry {
        padding: 0.5rem 1rem;
        background: var(--primary, #00d4aa);
        color: #000;
        border: none;
        border-radius: 6px;
        font-size: 0.8125rem;
        cursor: pointer;
        transition: background 0.15s;
    }
    
    .btn-retry:hover {
        background: #00e6b8;
    }
    
    .readme-content {
        background: var(--bg-elevated, #1a1a1a);
        border: 1px solid var(--border, #2d2d2d);
        border-radius: 10px;
        overflow: hidden;
    }
    
    .readme-raw {
        margin: 0;
        padding: 1.5rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.75rem;
        line-height: 1.6;
        color: var(--text-secondary, #a0a0a0);
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 600px;
        overflow-y: auto;
    }
</style>
