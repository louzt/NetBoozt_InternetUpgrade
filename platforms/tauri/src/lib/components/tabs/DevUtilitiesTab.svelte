<!--
    DevUtilitiesTab.svelte - Utilidades para desarrollador
    Testing de conexiones, curl, network tools
    By LOUST
-->
<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { invoke, isTauriAvailable } from '$lib/tauri-bridge';
    import Icon from '../Icon.svelte';
    
    const dispatch = createEventDispatcher();
    
    // Estado
    let isLoading = false;
    let activeSection: 'curl' | 'ping' | 'traceroute' | 'ports' | 'headers' = 'curl';
    
    // ====== CURL TESTING ======
    let curlUrl = 'https://api.ipify.org?format=json';
    let curlMethod = 'GET';
    let curlHeaders = '';
    let curlBody = '';
    let curlResult: {
        status?: number;
        time?: number;
        headers?: Record<string, string>;
        body?: string;
        error?: string;
    } | null = null;
    let curlHistory: Array<{ url: string; method: string; status: number; time: number; timestamp: Date }> = [];
    
    // ====== PING TEST ======
    let pingHost = '1.1.1.1';
    let pingCount = 4;
    let pingResults: Array<{ seq: number; ttl: number; time: number }> = [];
    let pingStats: { min: number; max: number; avg: number; loss: number } | null = null;
    let isPinging = false;
    
    // ====== TRACEROUTE ======
    let tracerouteHost = 'google.com';
    let tracerouteResults: Array<{ hop: number; ip: string; hostname?: string; time: number[] }> = [];
    let isTracing = false;
    
    // ====== PORT SCANNER ======
    let scanHost = 'localhost';
    let scanPorts = '80,443,8080,3000,5000';
    const PORT_PRESETS = {
        'Web': '80,443,8080,8443',
        'Dev': '3000,3001,4000,5000,5173,8000',
        'Database': '3306,5432,27017,6379,5984',
        'Common': '21,22,23,25,53,80,110,143,443,993,995',
        'Full Scan': '21,22,23,25,53,80,110,143,443,465,587,993,995,3000,3306,5000,5432,6379,8080,8443,27017'
    };
    let scanResults: Array<{ port: number; status: 'open' | 'closed' | 'filtered'; service?: string }> = [];
    let isScanning = false;
    
    // ====== HEADER CHECKER ======
    let headerUrl = 'https://google.com';
    let headerResults: Record<string, string> = {};
    let securityHeaders: Array<{ name: string; present: boolean; value?: string; recommendation?: string }> = [];
    let isCheckingHeaders = false;
    
    // Servicios comunes por puerto
    const PORT_SERVICES: Record<number, string> = {
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        465: 'SMTPS',
        587: 'SMTP',
        993: 'IMAPS',
        995: 'POP3S',
        3000: 'Dev Server',
        3306: 'MySQL',
        5000: 'Flask/Dev',
        5432: 'PostgreSQL',
        6379: 'Redis',
        8080: 'HTTP Alt',
        8443: 'HTTPS Alt',
        27017: 'MongoDB'
    };
    
    // Security Headers a verificar
    const SECURITY_HEADERS = [
        { name: 'Strict-Transport-Security', recommendation: 'HSTS - Fuerza conexiones HTTPS' },
        { name: 'Content-Security-Policy', recommendation: 'CSP - Protege contra XSS' },
        { name: 'X-Content-Type-Options', recommendation: 'Previene MIME sniffing' },
        { name: 'X-Frame-Options', recommendation: 'Protege contra clickjacking' },
        { name: 'X-XSS-Protection', recommendation: 'Filtro XSS del navegador' },
        { name: 'Referrer-Policy', recommendation: 'Controla info de referrer' },
        { name: 'Permissions-Policy', recommendation: 'Controla APIs del browser' },
    ];
    
    // ====== FUNCIONES ======
    async function runCurlRequest() {
        if (!curlUrl) return;
        isLoading = true;
        curlResult = null;
        
        const startTime = performance.now();
        
        try {
            if (isTauriAvailable()) {
                const result = await invoke<any>('http_request', {
                    url: curlUrl,
                    method: curlMethod,
                    headers: curlHeaders ? JSON.parse(curlHeaders) : {},
                    body: curlBody || null
                });
                
                curlResult = {
                    status: result.status,
                    time: performance.now() - startTime,
                    headers: result.headers,
                    body: typeof result.body === 'string' ? result.body : JSON.stringify(result.body, null, 2)
                };
            } else {
                // Mock para modo web
                const response = await fetch(curlUrl, {
                    method: curlMethod,
                    headers: curlHeaders ? JSON.parse(curlHeaders) : {},
                    body: curlMethod !== 'GET' && curlBody ? curlBody : undefined
                });
                
                const body = await response.text();
                const headers: Record<string, string> = {};
                response.headers.forEach((v, k) => headers[k] = v);
                
                curlResult = {
                    status: response.status,
                    time: performance.now() - startTime,
                    headers,
                    body
                };
            }
            
            // Guardar en historial
            curlHistory = [{
                url: curlUrl,
                method: curlMethod,
                status: curlResult.status || 0,
                time: curlResult.time || 0,
                timestamp: new Date()
            }, ...curlHistory.slice(0, 9)];
            
        } catch (e: any) {
            curlResult = {
                error: e.message || String(e),
                time: performance.now() - startTime
            };
        } finally {
            isLoading = false;
        }
    }
    
    async function runPing() {
        if (!pingHost || isPinging) return;
        isPinging = true;
        pingResults = [];
        pingStats = null;
        
        try {
            if (isTauriAvailable()) {
                const result = await invoke<any>('ping_multi', {
                    host: pingHost,
                    count: pingCount
                });
                pingResults = result.results;
                pingStats = result.stats;
            } else {
                // Mock para modo web
                const times: number[] = [];
                for (let i = 0; i < pingCount; i++) {
                    await new Promise(r => setTimeout(r, 100));
                    const time = Math.random() * 50 + 10;
                    times.push(time);
                    pingResults = [...pingResults, {
                        seq: i + 1,
                        ttl: 64,
                        time: time
                    }];
                }
                pingStats = {
                    min: Math.min(...times),
                    max: Math.max(...times),
                    avg: times.reduce((a, b) => a + b, 0) / times.length,
                    loss: 0
                };
            }
        } catch (e: any) {
            console.error('Ping error:', e);
        } finally {
            isPinging = false;
        }
    }
    
    async function runTraceroute() {
        if (!tracerouteHost || isTracing) return;
        isTracing = true;
        tracerouteResults = [];
        
        try {
            if (isTauriAvailable()) {
                const result = await invoke<any>('traceroute', {
                    host: tracerouteHost,
                    maxHops: 30
                });
                tracerouteResults = result.hops;
            } else {
                // Mock para modo web
                const mockHops = [
                    { hop: 1, ip: '192.168.1.1', hostname: 'router.local', time: [1.2, 1.5, 1.3] },
                    { hop: 2, ip: '10.0.0.1', time: [5.4, 6.2, 5.8] },
                    { hop: 3, ip: '72.14.223.168', hostname: 'google-isp.net', time: [12.3, 11.8, 12.1] },
                    { hop: 4, ip: '142.250.185.46', hostname: 'google.com', time: [15.2, 14.9, 15.0] },
                ];
                
                for (const hop of mockHops) {
                    await new Promise(r => setTimeout(r, 300));
                    tracerouteResults = [...tracerouteResults, hop];
                }
            }
        } catch (e: any) {
            console.error('Traceroute error:', e);
        } finally {
            isTracing = false;
        }
    }
    
    async function runPortScan() {
        if (!scanHost || isScanning) return;
        isScanning = true;
        scanResults = [];
        
        const ports = scanPorts.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p));
        
        try {
            if (isTauriAvailable()) {
                const result = await invoke<any>('scan_ports', {
                    host: scanHost,
                    ports
                });
                scanResults = result.results.map((r: any) => ({
                    ...r,
                    service: PORT_SERVICES[r.port] || 'Unknown'
                }));
            } else {
                // Mock para modo web
                for (const port of ports) {
                    await new Promise(r => setTimeout(r, 100));
                    const status = Math.random() > 0.7 ? 'open' : 'closed';
                    scanResults = [...scanResults, {
                        port,
                        status: status as 'open' | 'closed',
                        service: PORT_SERVICES[port] || 'Unknown'
                    }];
                }
            }
        } catch (e: any) {
            console.error('Port scan error:', e);
        } finally {
            isScanning = false;
        }
    }
    
    async function checkSecurityHeaders() {
        if (!headerUrl || isCheckingHeaders) return;
        isCheckingHeaders = true;
        headerResults = {};
        securityHeaders = [];
        
        try {
            let headers: Record<string, string> = {};
            
            if (isTauriAvailable()) {
                const result = await invoke<any>('get_headers', {
                    url: headerUrl
                });
                headers = result.headers;
            } else {
                // Mock para modo web (CORS limitará esto)
                try {
                    const response = await fetch(headerUrl, { method: 'HEAD', mode: 'no-cors' });
                    response.headers.forEach((v, k) => headers[k] = v);
                } catch {
                    // Si CORS falla, usar mock
                    headers = {
                        'content-type': 'text/html',
                        'server': 'nginx',
                        'strict-transport-security': 'max-age=31536000',
                    };
                }
            }
            
            headerResults = headers;
            
            // Verificar security headers
            securityHeaders = SECURITY_HEADERS.map(sh => ({
                name: sh.name,
                present: Object.keys(headers).some(k => k.toLowerCase() === sh.name.toLowerCase()),
                value: Object.entries(headers).find(([k]) => k.toLowerCase() === sh.name.toLowerCase())?.[1],
                recommendation: sh.recommendation
            }));
            
        } catch (e: any) {
            console.error('Header check error:', e);
        } finally {
            isCheckingHeaders = false;
        }
    }
    
    function formatTime(ms: number): string {
        if (ms < 1) return `${(ms * 1000).toFixed(0)}µs`;
        if (ms < 1000) return `${ms.toFixed(1)}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    }
    
    function getStatusColor(status: number): string {
        if (status >= 200 && status < 300) return '#00d4aa';
        if (status >= 300 && status < 400) return '#fdcb6e';
        if (status >= 400 && status < 500) return '#ff9800';
        return '#ff6b6b';
    }
    
    // Evaluar salud del ping basado en latencia
    function getPingHealth(avg: number, loss: number): { status: string; color: string; emoji: string; description: string } {
        if (loss > 10) return { status: 'Malo', color: '#ff6b6b', emoji: '🔴', description: 'Pérdida de paquetes alta' };
        if (loss > 0) return { status: 'Inestable', color: '#ff9800', emoji: '🟠', description: 'Hay pérdida de paquetes' };
        if (avg < 20) return { status: 'Excelente', color: '#00d4aa', emoji: '🟢', description: 'Latencia muy baja, ideal para gaming' };
        if (avg < 50) return { status: 'Muy Bueno', color: '#00d4aa', emoji: '🟢', description: 'Latencia baja, excelente para la mayoría de usos' };
        if (avg < 100) return { status: 'Bueno', color: '#fdcb6e', emoji: '🟡', description: 'Latencia aceptable para uso general' };
        if (avg < 150) return { status: 'Aceptable', color: '#fdcb6e', emoji: '🟡', description: 'Latencia moderada, puede haber lag en juegos' };
        if (avg < 250) return { status: 'Lento', color: '#ff9800', emoji: '🟠', description: 'Latencia alta, noticeable en videollamadas' };
        return { status: 'Muy Lento', color: '#ff6b6b', emoji: '🔴', description: 'Latencia muy alta, conexión problemática' };
    }
    
    // Limpiar historiales
    function clearCurlHistory() { curlHistory = []; }
    function clearPingResults() { pingResults = []; pingStats = null; }
    function clearTraceroute() { tracerouteResults = []; }
    function clearPortScan() { scanResults = []; }
    function clearHeaders() { headerResults = {}; securityHeaders = []; }
</script>

<div class="dev-utilities">
    <!-- Navigation Pills -->
    <nav class="section-nav">
        <button 
            class="nav-pill" 
            class:active={activeSection === 'curl'}
            on:click={() => activeSection = 'curl'}
        >
            <Icon name="code" size={14} />
            cURL
        </button>
        <button 
            class="nav-pill" 
            class:active={activeSection === 'ping'}
            on:click={() => activeSection = 'ping'}
        >
            <Icon name="activity" size={14} />
            Ping
        </button>
        <button 
            class="nav-pill" 
            class:active={activeSection === 'traceroute'}
            on:click={() => activeSection = 'traceroute'}
        >
            <Icon name="share-2" size={14} />
            Traceroute
        </button>
        <button 
            class="nav-pill" 
            class:active={activeSection === 'ports'}
            on:click={() => activeSection = 'ports'}
        >
            <Icon name="server" size={14} />
            Ports
        </button>
        <button 
            class="nav-pill" 
            class:active={activeSection === 'headers'}
            on:click={() => activeSection = 'headers'}
        >
            <Icon name="shield" size={14} />
            Headers
        </button>
    </nav>
    
    <!-- Content -->
    <div class="content">
        {#if activeSection === 'curl'}
            <!-- cURL Testing -->
            <section class="tool-section">
                <div class="tool-header">
                    <h3><Icon name="code" size={16} /> HTTP Request Tester</h3>
                    <p>Prueba endpoints y APIs con peticiones HTTP personalizadas</p>
                </div>
                
                <div class="curl-form">
                    <div class="form-row">
                        <select bind:value={curlMethod} class="method-select">
                            <option>GET</option>
                            <option>POST</option>
                            <option>PUT</option>
                            <option>PATCH</option>
                            <option>DELETE</option>
                            <option>HEAD</option>
                            <option>OPTIONS</option>
                        </select>
                        <input 
                            type="text" 
                            bind:value={curlUrl} 
                            placeholder="https://api.example.com/endpoint"
                            class="url-input"
                        />
                        <button 
                            class="btn-send" 
                            on:click={runCurlRequest}
                            disabled={isLoading || !curlUrl}
                        >
                            {#if isLoading}
                                <span class="spinner"></span>
                            {:else}
                                <Icon name="send" size={14} />
                            {/if}
                            Enviar
                        </button>
                    </div>
                    
                    <details class="advanced-options">
                        <summary>Opciones avanzadas</summary>
                        <div class="options-grid">
                            <div class="option-group">
                                <label for="curlHeaders">Headers (JSON)</label>
                                <textarea 
                                    id="curlHeaders"
                                    bind:value={curlHeaders} 
                                    placeholder={'{"Authorization": "Bearer token"}'}
                                    rows="3"
                                ></textarea>
                            </div>
                            {#if curlMethod !== 'GET' && curlMethod !== 'HEAD'}
                                <div class="option-group">
                                    <label for="curlBody">Body</label>
                                    <textarea 
                                        id="curlBody"
                                        bind:value={curlBody} 
                                        placeholder={'{"key": "value"}'}
                                        rows="3"
                                    ></textarea>
                                </div>
                            {/if}
                        </div>
                    </details>
                </div>
                
                {#if curlResult}
                    <div class="result-panel" class:error={curlResult.error}>
                        {#if curlResult.error}
                            <div class="result-header error">
                                <Icon name="x-circle" size={18} />
                                <span>Error: {curlResult.error}</span>
                            </div>
                        {:else}
                            <div class="result-header">
                                <span class="status-badge" style="background: {getStatusColor(curlResult.status || 0)}">
                                    {curlResult.status}
                                </span>
                                <span class="time-badge">
                                    <Icon name="clock" size={12} />
                                    {formatTime(curlResult.time || 0)}
                                </span>
                            </div>
                            
                            {#if curlResult.headers}
                                <details class="response-section">
                                    <summary>Headers ({Object.keys(curlResult.headers).length})</summary>
                                    <pre class="headers-pre">{JSON.stringify(curlResult.headers, null, 2)}</pre>
                                </details>
                            {/if}
                            
                            <div class="response-body">
                                <span class="response-label">Response Body</span>
                                <pre class="body-pre">{curlResult.body}</pre>
                            </div>
                        {/if}
                    </div>
                {/if}
                
                {#if curlHistory.length > 0}
                    <div class="history-section">
                        <div class="history-header">
                            <h4><Icon name="clock" size={14} /> Historial reciente</h4>
                            <button class="btn-clear-sm" on:click={clearCurlHistory} title="Limpiar historial">
                                <Icon name="trash-2" size={11} />
                            </button>
                        </div>
                        <div class="history-list">
                            {#each curlHistory as item}
                                <button 
                                    class="history-item"
                                    on:click={() => { curlUrl = item.url; curlMethod = item.method; }}
                                >
                                    <span class="history-method">{item.method}</span>
                                    <span class="history-url">{item.url}</span>
                                    <span class="history-status" style="color: {getStatusColor(item.status)}">{item.status}</span>
                                    <span class="history-time">{formatTime(item.time)}</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}
            </section>
            
        {:else if activeSection === 'ping'}
            <!-- Ping Test -->
            <section class="tool-section">
                <div class="tool-header">
                    <div class="tool-title-row">
                        <h3><Icon name="activity" size={16} /> Ping Test</h3>
                        {#if pingResults.length > 0}
                            <button class="btn-clear" on:click={clearPingResults} title="Limpiar resultados">
                                <Icon name="trash-2" size={12} /> Limpiar
                            </button>
                        {/if}
                    </div>
                    <p>Mide la latencia y conectividad a un host</p>
                </div>
                
                <div class="ping-form">
                    <input 
                        type="text" 
                        bind:value={pingHost} 
                        placeholder="Host o IP (ej: 1.1.1.1)"
                        class="host-input"
                    />
                    <div class="count-selector">
                        <label for="ping-count">Paquetes:</label>
                        <select id="ping-count" bind:value={pingCount}>
                            <option value={4}>4</option>
                            <option value={8}>8</option>
                            <option value={16}>16</option>
                            <option value={32}>32</option>
                        </select>
                    </div>
                    <button 
                        class="btn-action" 
                        on:click={runPing}
                        disabled={isPinging || !pingHost}
                    >
                        {#if isPinging}
                            <span class="spinner"></span>
                        {:else}
                            <Icon name="radio" size={14} />
                        {/if}
                        Ping
                    </button>
                </div>
                
                {#if pingResults.length > 0}
                    <div class="ping-results">
                        <div class="ping-graph">
                            {#each pingResults as result}
                                <div 
                                    class="ping-bar"
                                    style="--height: {Math.min(result.time / 100 * 100, 100)}%"
                                    title="{result.seq}: {result.time.toFixed(1)}ms"
                                >
                                    <span class="bar-value">{result.time.toFixed(0)}</span>
                                </div>
                            {/each}
                        </div>
                        
                        {#if pingStats}
                            {@const health = getPingHealth(pingStats.avg, pingStats.loss)}
                            <div class="ping-health-card" style="--health-color: {health.color}">
                                <span class="health-emoji">{health.emoji}</span>
                                <div class="health-info">
                                    <span class="health-status">{health.status}</span>
                                    <span class="health-desc">{health.description}</span>
                                </div>
                            </div>
                            
                            <div class="ping-stats">
                                <div class="stat-item">
                                    <span class="stat-label">Min</span>
                                    <span class="stat-value good">{pingStats.min.toFixed(1)}ms</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Avg</span>
                                    <span class="stat-value">{pingStats.avg.toFixed(1)}ms</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Max</span>
                                    <span class="stat-value warning">{pingStats.max.toFixed(1)}ms</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Loss</span>
                                    <span class="stat-value" class:error={pingStats.loss > 0}>{pingStats.loss}%</span>
                                </div>
                            </div>
                            
                            <div class="ping-interpretation">
                                <Icon name="info" size={12} />
                                <span>Jitter: {(pingStats.max - pingStats.min).toFixed(1)}ms • 
                                    {pingStats.avg < 50 ? 'Bueno para gaming y videollamadas' : 
                                     pingStats.avg < 100 ? 'Aceptable para uso general' : 
                                     'Puede experimentar lag en aplicaciones en tiempo real'}
                                </span>
                            </div>
                        {/if}
                    </div>
                {/if}
            </section>
            
        {:else if activeSection === 'traceroute'}
            <!-- Traceroute -->
            <section class="tool-section">
                <div class="tool-header">
                    <div class="tool-title-row">
                        <h3><Icon name="share-2" size={16} /> Traceroute</h3>
                        {#if tracerouteResults.length > 0 && !isTracing}
                            <button class="btn-clear" on:click={clearTraceroute} title="Limpiar resultados">
                                <Icon name="trash-2" size={12} /> Limpiar
                            </button>
                        {/if}
                    </div>
                    <p>Visualiza la ruta de paquetes hasta el destino (puede tardar 30-60 segundos)</p>
                </div>
                
                <div class="trace-form">
                    <input 
                        type="text" 
                        bind:value={tracerouteHost} 
                        placeholder="Host o dominio (ej: google.com)"
                        class="host-input"
                    />
                    <button 
                        class="btn-action" 
                        on:click={runTraceroute}
                        disabled={isTracing || !tracerouteHost}
                    >
                        {#if isTracing}
                            <span class="spinner"></span>
                        {:else}
                            <Icon name="play" size={14} />
                        {/if}
                        Trace
                    </button>
                </div>
                
                {#if tracerouteResults.length > 0 || isTracing}
                    <div class="trace-results">
                        <div class="trace-path">
                            {#each tracerouteResults as hop}
                                <div class="trace-hop">
                                    <span class="hop-number">{hop.hop}</span>
                                    <div class="hop-info">
                                        <span class="hop-ip">{hop.ip}</span>
                                        {#if hop.hostname}
                                            <span class="hop-hostname">{hop.hostname}</span>
                                        {/if}
                                    </div>
                                    <div class="hop-times">
                                        {#each hop.time as t}
                                            <span class="hop-time">{t.toFixed(1)}ms</span>
                                        {/each}
                                    </div>
                                </div>
                            {/each}
                            {#if isTracing}
                                <div class="trace-progress">
                                    <div class="progress-indicator">
                                        <span class="spinner-sm"></span>
                                        <div class="progress-info">
                                            <span class="progress-title">Trazando ruta a {tracerouteHost}...</span>
                                            <span class="progress-detail">
                                                Hop {tracerouteResults.length + 1} de ~30 • Esto puede tardar hasta 60 segundos
                                            </span>
                                        </div>
                                    </div>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: {Math.min((tracerouteResults.length / 30) * 100, 95)}%"></div>
                                    </div>
                                </div>
                            {:else if tracerouteResults.length > 0}
                                <div class="trace-summary">
                                    <Icon name="check-circle" size={14} color="#00d4aa" />
                                    <span>Ruta completa: {tracerouteResults.length} saltos en {tracerouteResults.reduce((sum, h) => sum + (h.time[0] || 0), 0).toFixed(0)}ms total</span>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/if}
            </section>
            
        {:else if activeSection === 'ports'}
            <!-- Port Scanner -->
            <section class="tool-section">
                <div class="tool-header">
                    <div class="tool-title-row">
                        <h3><Icon name="server" size={16} /> Port Scanner</h3>
                        {#if scanResults.length > 0}
                            <button class="btn-clear" on:click={clearPortScan} title="Limpiar resultados">
                                <Icon name="trash-2" size={12} /> Limpiar
                            </button>
                        {/if}
                    </div>
                    <p>Escanea puertos abiertos en un host</p>
                </div>
                
                <!-- Presets de puertos -->
                <div class="port-presets">
                    <span class="presets-label">Presets:</span>
                    {#each Object.entries(PORT_PRESETS) as [name, ports]}
                        <button 
                            class="preset-btn" 
                            class:active={scanPorts === ports}
                            on:click={() => scanPorts = ports}
                        >{name}</button>
                    {/each}
                </div>
                
                <div class="scan-form">
                    <input 
                        type="text" 
                        bind:value={scanHost} 
                        placeholder="Host (ej: localhost, 192.168.1.1)"
                        class="host-input"
                    />
                    <input 
                        type="text" 
                        bind:value={scanPorts} 
                        placeholder="Puertos (ej: 80,443,8080 o rango 80-100)"
                        class="ports-input wide"
                    />
                    <button 
                        class="btn-action" 
                        on:click={runPortScan}
                        disabled={isScanning || !scanHost}
                    >
                        {#if isScanning}
                            <span class="spinner"></span>
                        {:else}
                            <Icon name="search" size={14} />
                        {/if}
                        Escanear
                    </button>
                </div>
                
                {#if scanResults.length > 0}
                    <div class="scan-results">
                        <div class="ports-grid">
                            {#each scanResults as result}
                                <div class="port-card" class:open={result.status === 'open'} class:closed={result.status === 'closed'}>
                                    <span class="port-number">{result.port}</span>
                                    <span class="port-service">{result.service}</span>
                                    <span class="port-status" class:open={result.status === 'open'}>
                                        {result.status === 'open' ? '● Abierto' : '○ Cerrado'}
                                    </span>
                                </div>
                            {/each}
                        </div>
                        
                        <div class="scan-summary">
                            <span class="summary-item open">
                                <Icon name="check-circle" size={14} />
                                {scanResults.filter(r => r.status === 'open').length} abiertos
                            </span>
                            <span class="summary-item closed">
                                <Icon name="x-circle" size={14} />
                                {scanResults.filter(r => r.status === 'closed').length} cerrados
                            </span>
                        </div>
                    </div>
                {/if}
            </section>
            
        {:else if activeSection === 'headers'}
            <!-- Security Headers Checker -->
            <section class="tool-section">
                <div class="tool-header">
                    <div class="tool-title-row">
                        <h3><Icon name="shield" size={16} /> Security Headers</h3>
                        {#if securityHeaders.length > 0}
                            <button class="btn-clear" on:click={clearHeaders} title="Limpiar resultados">
                                <Icon name="trash-2" size={12} /> Limpiar
                            </button>
                        {/if}
                    </div>
                    <p>Analiza las cabeceras de seguridad de un sitio web</p>
                </div>
                
                <div class="header-form">
                    <input 
                        type="text" 
                        bind:value={headerUrl} 
                        placeholder="URL (ej: https://google.com)"
                        class="url-input wide"
                    />
                    <button 
                        class="btn-action" 
                        on:click={checkSecurityHeaders}
                        disabled={isCheckingHeaders || !headerUrl}
                    >
                        {#if isCheckingHeaders}
                            <span class="spinner"></span>
                        {:else}
                            <Icon name="shield" size={14} />
                        {/if}
                        Analizar
                    </button>
                </div>
                
                {#if securityHeaders.length > 0}
                    <div class="headers-results">
                        <div class="security-score">
                            <div class="score-ring" style="--score: {securityHeaders.filter(h => h.present).length / securityHeaders.length * 100}%">
                                <span class="score-value">{securityHeaders.filter(h => h.present).length}/{securityHeaders.length}</span>
                            </div>
                            <span class="score-label">Headers de Seguridad</span>
                        </div>
                        
                        <div class="security-list">
                            {#each securityHeaders as header}
                                <div class="security-item" class:present={header.present} class:missing={!header.present}>
                                    <div class="header-status">
                                        {#if header.present}
                                            <Icon name="check-circle" size={16} color="#00d4aa" />
                                        {:else}
                                            <Icon name="x-circle" size={16} color="#ff6b6b" />
                                        {/if}
                                    </div>
                                    <div class="header-info">
                                        <span class="header-name">{header.name}</span>
                                        {#if header.value}
                                            <span class="header-value">{header.value}</span>
                                        {:else}
                                            <span class="header-recommendation">{header.recommendation}</span>
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}
                
                {#if Object.keys(headerResults).length > 0}
                    <details class="all-headers">
                        <summary>Todas las cabeceras ({Object.keys(headerResults).length})</summary>
                        <pre class="headers-pre">{JSON.stringify(headerResults, null, 2)}</pre>
                    </details>
                {/if}
            </section>
        {/if}
    </div>
</div>

<style>
    .dev-utilities {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        height: 100%;
        overflow: hidden;
    }
    
    /* Navigation */
    .section-nav {
        display: flex;
        gap: 0.5rem;
        padding: 0.5rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
    }
    
    .nav-pill {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.5rem 1rem;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .nav-pill:hover {
        background: rgba(255, 255, 255, 0.08);
        color: var(--text-primary, #fff);
    }
    
    .nav-pill.active {
        background: var(--primary, #00d4aa);
        color: #000;
    }
    
    /* Content */
    .content {
        flex: 1;
        overflow-y: auto;
    }
    
    .tool-section {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .tool-header h3 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0 0 0.25rem 0;
        font-size: 1rem;
        color: var(--text-primary, #fff);
    }
    
    .tool-header p {
        margin: 0;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    /* Forms */
    .curl-form, .ping-form, .trace-form, .scan-form, .header-form {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .form-row {
        display: flex;
        gap: 0.5rem;
    }
    
    .method-select {
        width: 100px;
        padding: 0.625rem 0.75rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        color: var(--primary, #00d4aa);
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .url-input, .host-input, .ports-input {
        flex: 1;
        padding: 0.625rem 0.875rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        color: var(--text-primary, #fff);
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .url-input.wide {
        flex: 1;
    }
    
    .url-input:focus, .host-input:focus, .ports-input:focus {
        outline: none;
        border-color: var(--primary, #00d4aa);
    }
    
    .btn-send, .btn-action {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.625rem 1.25rem;
        background: var(--primary, #00d4aa);
        border: none;
        border-radius: 8px;
        color: #000;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-send:hover:not(:disabled), .btn-action:hover:not(:disabled) {
        filter: brightness(1.1);
    }
    
    .btn-send:disabled, .btn-action:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    
    /* Advanced Options */
    .advanced-options {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .advanced-options summary {
        padding: 0.5rem;
        cursor: pointer;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.75rem;
    }
    
    .options-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        padding: 0.5rem;
    }
    
    .option-group label {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin-bottom: 0.35rem;
    }
    
    .option-group textarea {
        width: 100%;
        padding: 0.5rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        resize: vertical;
    }
    
    /* Result Panel */
    .result-panel {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 12px;
        overflow: hidden;
    }
    
    .result-panel.error {
        border-color: rgba(255, 107, 107, 0.3);
    }
    
    .result-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid var(--border, #3d3d3d);
    }
    
    .result-header.error {
        color: var(--error, #ff6b6b);
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        color: #000;
    }
    
    .time-badge {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .response-section {
        padding: 0.5rem 1rem;
    }
    
    .response-section summary {
        cursor: pointer;
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .headers-pre, .body-pre {
        margin: 0.5rem 0;
        padding: 0.75rem;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 6px;
        font-size: 0.7rem;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-all;
    }
    
    .response-body {
        padding: 0.75rem 1rem;
    }
    
    .response-body .response-label {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin-bottom: 0.35rem;
    }
    
    /* History */
    .history-section {
        margin-top: 1rem;
    }
    
    .history-section h4 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0 0 0.5rem 0;
        font-size: 0.8rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    .history-list {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    
    .history-item {
        display: grid;
        grid-template-columns: 60px 1fr 50px 70px;
        gap: 0.5rem;
        align-items: center;
        padding: 0.5rem 0.75rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid transparent;
        border-radius: 6px;
        cursor: pointer;
        text-align: left;
        transition: all 0.2s;
    }
    
    .history-item:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: var(--border, #3d3d3d);
    }
    
    .history-method {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--primary, #00d4aa);
    }
    
    .history-url {
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .history-status {
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .history-time {
        font-size: 0.65rem;
        color: var(--text-muted, #666);
    }
    
    /* Ping */
    .ping-form, .trace-form, .scan-form, .header-form {
        flex-direction: row;
        align-items: center;
    }
    
    .count-selector {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .count-selector label {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .count-selector select {
        padding: 0.5rem;
        background: var(--bg-elevated, #2b2b2b);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 6px;
        color: var(--text-primary, #fff);
        font-size: 0.8rem;
    }
    
    .ping-results {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .ping-graph {
        display: flex;
        align-items: flex-end;
        gap: 0.5rem;
        height: 120px;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
    }
    
    .ping-bar {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        height: var(--height);
        min-height: 20px;
        background: linear-gradient(to top, var(--primary, #00d4aa), rgba(0, 212, 170, 0.3));
        border-radius: 4px 4px 0 0;
        transition: height 0.3s ease;
    }
    
    .bar-value {
        font-size: 0.6rem;
        color: var(--text-primary, #fff);
        padding: 0.25rem;
    }
    
    .ping-stats {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
    
    .stat-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.25rem;
    }
    
    .stat-label {
        font-size: 0.65rem;
        color: var(--text-muted, #666);
        text-transform: uppercase;
    }
    
    .stat-value {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stat-value.good { color: var(--primary, #00d4aa); }
    .stat-value.warning { color: var(--warning, #fdcb6e); }
    .stat-value.error { color: var(--error, #ff6b6b); }
    
    /* Traceroute */
    .trace-results {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .trace-path {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .trace-hop {
        display: grid;
        grid-template-columns: 30px 1fr auto;
        gap: 1rem;
        align-items: center;
        padding: 0.5rem 0.75rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
    }
    
    .hop-number {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--primary, #00d4aa);
        color: #000;
        border-radius: 50%;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .hop-info {
        display: flex;
        flex-direction: column;
    }
    
    .hop-ip {
        font-size: 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary, #fff);
    }
    
    .hop-hostname {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .hop-times {
        display: flex;
        gap: 0.5rem;
    }
    
    .hop-time {
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Port Scanner */
    .ports-input {
        width: 200px;
        flex: 0;
    }
    
    .ports-input.wide {
        width: auto;
        flex: 1;
    }
    
    /* Tool header with clear button */
    .tool-title-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
    }
    
    .btn-clear {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.35rem 0.6rem;
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-radius: 6px;
        color: var(--error, #ff6b6b);
        font-size: 0.7rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-clear:hover {
        background: rgba(255, 107, 107, 0.2);
    }
    
    .btn-clear-sm {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.25rem;
        background: transparent;
        border: none;
        color: var(--text-muted, #666);
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.2s;
    }
    
    .btn-clear-sm:hover {
        color: var(--error, #ff6b6b);
        background: rgba(255, 107, 107, 0.1);
    }
    
    .history-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    
    .history-header h4 {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
        font-size: 0.8rem;
        color: var(--text-secondary, #a0a0a0);
    }
    
    /* Ping health card */
    .ping-health-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--health-color);
        border-left: 4px solid var(--health-color);
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .health-emoji {
        font-size: 1.5rem;
    }
    
    .health-info {
        display: flex;
        flex-direction: column;
    }
    
    .health-status {
        font-size: 0.9rem;
        font-weight: 700;
        color: var(--health-color);
    }
    
    .health-desc {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .ping-interpretation {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(0, 212, 170, 0.05);
        border-radius: 6px;
        font-size: 0.7rem;
        color: var(--text-secondary, #a0a0a0);
        margin-top: 0.75rem;
    }
    
    /* Traceroute progress */
    .trace-progress {
        padding: 1rem;
        background: rgba(0, 212, 170, 0.05);
        border: 1px solid rgba(0, 212, 170, 0.2);
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    
    .progress-indicator {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .progress-info {
        display: flex;
        flex-direction: column;
    }
    
    .progress-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .progress-detail {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .progress-bar {
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 2px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary, #00d4aa), #00b894);
        border-radius: 2px;
        transition: width 0.5s ease;
    }
    
    .trace-summary {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: rgba(0, 212, 170, 0.1);
        border-radius: 6px;
        font-size: 0.75rem;
        color: var(--primary, #00d4aa);
        margin-top: 0.5rem;
    }
    
    /* Port presets */
    .port-presets {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .presets-label {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .preset-btn {
        padding: 0.3rem 0.6rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 4px;
        color: var(--text-secondary, #a0a0a0);
        font-size: 0.65rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .preset-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: var(--primary, #00d4aa);
    }
    
    .preset-btn.active {
        background: rgba(0, 212, 170, 0.2);
        border-color: var(--primary, #00d4aa);
        color: var(--primary, #00d4aa);
    }
    
    .scan-results {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .ports-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 0.5rem;
    }
    
    .port-card {
        display: flex;
        flex-direction: column;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--border, #3d3d3d);
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .port-card.open {
        border-color: rgba(0, 212, 170, 0.3);
        background: rgba(0, 212, 170, 0.05);
    }
    
    .port-number {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .port-service {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .port-status {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
        margin-top: 0.5rem;
    }
    
    .port-status.open {
        color: var(--primary, #00d4aa);
    }
    
    .scan-summary {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
    
    .summary-item {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.8rem;
    }
    
    .summary-item.open { color: var(--primary, #00d4aa); }
    .summary-item.closed { color: var(--text-muted, #666); }
    
    /* Security Headers */
    .headers-results {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .security-score {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }
    
    .score-ring {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: conic-gradient(
            var(--primary, #00d4aa) 0% var(--score),
            rgba(255, 255, 255, 0.1) var(--score) 100%
        );
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .score-value {
        width: 60px;
        height: 60px;
        background: var(--bg-elevated, #1a1a1a);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary, #fff);
    }
    
    .score-label {
        font-size: 0.75rem;
        color: var(--text-muted, #666);
    }
    
    .security-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .security-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
    }
    
    .security-item.present {
        border-left: 3px solid var(--primary, #00d4aa);
    }
    
    .security-item.missing {
        border-left: 3px solid var(--error, #ff6b6b);
        opacity: 0.7;
    }
    
    .header-status {
        flex-shrink: 0;
    }
    
    .header-info {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }
    
    .header-name {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-primary, #fff);
    }
    
    .header-value {
        font-size: 0.7rem;
        color: var(--primary, #00d4aa);
        font-family: 'JetBrains Mono', monospace;
        word-break: break-all;
    }
    
    .header-recommendation {
        font-size: 0.7rem;
        color: var(--text-muted, #666);
    }
    
    .all-headers {
        margin-top: 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .all-headers summary {
        cursor: pointer;
        font-size: 0.75rem;
        color: var(--text-secondary, #a0a0a0);
        padding: 0.5rem;
    }
    
    /* Spinner */
    .spinner {
        width: 14px;
        height: 14px;
        border: 2px solid rgba(0, 0, 0, 0.2);
        border-top-color: currentColor;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    .spinner-sm {
        width: 12px;
        height: 12px;
        border: 1.5px solid var(--border, #3d3d3d);
        border-top-color: var(--text-muted, #888);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
