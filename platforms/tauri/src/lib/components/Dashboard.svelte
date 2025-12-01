<!-- NetBoozt Dashboard Component -->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from '@tauri-apps/api/tauri';
  
  interface NetworkAdapter {
    name: string;
    description: string;
    status: string;
    link_speed: string;
    mac_address: string;
  }
  
  interface DiagnosticResult {
    health: string;
    failure_point: string;
    adapter_ok: boolean;
    adapter_name: string;
    router_ok: boolean;
    router_latency_ms: number;
    isp_ok: boolean;
    isp_latency_ms: number;
    dns_ok: boolean;
    dns_latency_ms: number;
    recommendation: string;
  }
  
  let adapters: NetworkAdapter[] = [];
  let diagnostic: DiagnosticResult | null = null;
  let loading = true;
  let diagnosing = false;
  let error: string | null = null;
  
  // Refresh interval
  let refreshInterval: number;
  
  onMount(async () => {
    await loadAdapters();
    refreshInterval = setInterval(quickCheck, 30000) as unknown as number;
  });
  
  onDestroy(() => {
    if (refreshInterval) clearInterval(refreshInterval);
  });
  
  async function loadAdapters() {
    try {
      loading = true;
      adapters = await invoke('get_network_adapters');
      error = null;
    } catch (e) {
      error = `Error: ${e}`;
    } finally {
      loading = false;
    }
  }
  
  async function runDiagnostic() {
    try {
      diagnosing = true;
      diagnostic = await invoke('run_full_diagnostic');
    } catch (e) {
      error = `Diagnostic error: ${e}`;
    } finally {
      diagnosing = false;
    }
  }
  
  async function quickCheck() {
    try {
      const [ok, msg]: [boolean, string] = await invoke('quick_check');
      // Update status indicator
    } catch (e) {
      console.error('Quick check failed:', e);
    }
  }
  
  async function setDns(provider: string) {
    if (adapters.length === 0) return;
    
    const dnsMap: Record<string, [string, string]> = {
      cloudflare: ['1.1.1.1', '1.0.0.1'],
      google: ['8.8.8.8', '8.8.4.4'],
      quad9: ['9.9.9.9', '149.112.112.112'],
    };
    
    const [primary, secondary] = dnsMap[provider] || dnsMap.cloudflare;
    
    try {
      await invoke('set_dns_servers', {
        adapter: adapters[0].name,
        primary,
        secondary,
      });
      await invoke('flush_dns_cache');
    } catch (e) {
      error = `DNS change failed: ${e}`;
    }
  }
  
  function getHealthColor(health: string): string {
    const colors: Record<string, string> = {
      Excellent: '#00d4aa',
      Good: '#4CAF50',
      Fair: '#FFC107',
      Poor: '#FF9800',
      Bad: '#F44336',
      Down: '#9E9E9E',
    };
    return colors[health] || '#9E9E9E';
  }
</script>

<div class="dashboard">
  <header>
    <h1>🚀 NetBoozt</h1>
    <span class="subtitle">Network Optimization Tool</span>
  </header>
  
  {#if error}
    <div class="error-banner">
      ⚠️ {error}
      <button on:click={() => error = null}>✕</button>
    </div>
  {/if}
  
  <section class="adapters">
    <h2>📡 Network Adapters</h2>
    
    {#if loading}
      <div class="loading">Loading...</div>
    {:else if adapters.length === 0}
      <div class="empty">No active network adapters found</div>
    {:else}
      <div class="adapter-grid">
        {#each adapters as adapter}
          <div class="adapter-card">
            <h3>{adapter.name}</h3>
            <p class="description">{adapter.description}</p>
            <div class="stats">
              <span class="status status-{adapter.status.toLowerCase()}">{adapter.status}</span>
              <span class="speed">{adapter.link_speed}</span>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>
  
  <section class="quick-actions">
    <h2>⚡ Quick Actions</h2>
    
    <div class="action-grid">
      <button class="action-btn primary" on:click={runDiagnostic} disabled={diagnosing}>
        {#if diagnosing}
          🔄 Diagnosing...
        {:else}
          🔍 Run Diagnostic
        {/if}
      </button>
      
      <button class="action-btn" on:click={() => setDns('cloudflare')}>
        🌐 Use Cloudflare DNS
      </button>
      
      <button class="action-btn" on:click={() => setDns('google')}>
        🔵 Use Google DNS
      </button>
      
      <button class="action-btn" on:click={() => invoke('flush_dns_cache')}>
        🧹 Flush DNS Cache
      </button>
    </div>
  </section>
  
  {#if diagnostic}
    <section class="diagnostic-result">
      <h2>📊 Diagnostic Result</h2>
      
      <div class="health-indicator" style="--health-color: {getHealthColor(diagnostic.health)}">
        <span class="health-label">{diagnostic.health}</span>
      </div>
      
      <div class="chain">
        <div class="chain-step" class:ok={diagnostic.adapter_ok} class:fail={!diagnostic.adapter_ok}>
          <span class="icon">{diagnostic.adapter_ok ? '✅' : '❌'}</span>
          <span class="label">Adapter</span>
          <span class="detail">{diagnostic.adapter_name || 'N/A'}</span>
        </div>
        
        <div class="chain-arrow">→</div>
        
        <div class="chain-step" class:ok={diagnostic.router_ok} class:fail={!diagnostic.router_ok}>
          <span class="icon">{diagnostic.router_ok ? '✅' : '❌'}</span>
          <span class="label">Router</span>
          <span class="detail">{diagnostic.router_latency_ms.toFixed(0)}ms</span>
        </div>
        
        <div class="chain-arrow">→</div>
        
        <div class="chain-step" class:ok={diagnostic.isp_ok} class:fail={!diagnostic.isp_ok}>
          <span class="icon">{diagnostic.isp_ok ? '✅' : '❌'}</span>
          <span class="label">ISP</span>
          <span class="detail">{diagnostic.isp_latency_ms.toFixed(0)}ms</span>
        </div>
        
        <div class="chain-arrow">→</div>
        
        <div class="chain-step" class:ok={diagnostic.dns_ok} class:fail={!diagnostic.dns_ok}>
          <span class="icon">{diagnostic.dns_ok ? '✅' : '❌'}</span>
          <span class="label">DNS</span>
          <span class="detail">{diagnostic.dns_latency_ms.toFixed(0)}ms</span>
        </div>
      </div>
      
      <div class="recommendation">
        💡 {diagnostic.recommendation}
      </div>
    </section>
  {/if}
</div>

<style>
  .dashboard {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #ffffff;
    background: #1a1a1a;
    min-height: 100vh;
  }
  
  header {
    text-align: center;
    margin-bottom: 2rem;
  }
  
  header h1 {
    font-size: 2.5rem;
    margin: 0;
    color: #00d4aa;
  }
  
  .subtitle {
    color: #888;
    font-size: 1rem;
  }
  
  section {
    background: #2b2b2b;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  section h2 {
    margin: 0 0 1rem 0;
    font-size: 1.25rem;
    color: #ffffff;
  }
  
  .adapter-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }
  
  .adapter-card {
    background: #333;
    border-radius: 8px;
    padding: 1rem;
  }
  
  .adapter-card h3 {
    margin: 0 0 0.5rem 0;
    color: #00d4aa;
  }
  
  .adapter-card .description {
    color: #888;
    font-size: 0.875rem;
    margin: 0 0 0.5rem 0;
  }
  
  .adapter-card .stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .status {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    text-transform: uppercase;
  }
  
  .status-up {
    background: rgba(0, 212, 170, 0.2);
    color: #00d4aa;
  }
  
  .action-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 1rem;
  }
  
  .action-btn {
    padding: 1rem;
    border: none;
    border-radius: 8px;
    background: #444;
    color: #fff;
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s;
  }
  
  .action-btn:hover {
    background: #555;
    transform: translateY(-2px);
  }
  
  .action-btn.primary {
    background: #00d4aa;
    color: #000;
  }
  
  .action-btn.primary:hover {
    background: #00b894;
  }
  
  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .health-indicator {
    text-align: center;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .health-label {
    font-size: 2rem;
    font-weight: bold;
    color: var(--health-color);
  }
  
  .chain {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin: 1rem 0;
  }
  
  .chain-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    background: #333;
    border-radius: 8px;
    min-width: 100px;
  }
  
  .chain-step.ok {
    border: 2px solid #00d4aa;
  }
  
  .chain-step.fail {
    border: 2px solid #F44336;
  }
  
  .chain-step .icon {
    font-size: 1.5rem;
  }
  
  .chain-step .label {
    font-weight: bold;
    margin: 0.25rem 0;
  }
  
  .chain-step .detail {
    color: #888;
    font-size: 0.875rem;
  }
  
  .chain-arrow {
    color: #555;
    font-size: 1.5rem;
  }
  
  .recommendation {
    background: rgba(0, 212, 170, 0.1);
    border-left: 4px solid #00d4aa;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
  }
  
  .error-banner {
    background: rgba(244, 67, 54, 0.2);
    border: 1px solid #F44336;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .error-banner button {
    background: none;
    border: none;
    color: #F44336;
    cursor: pointer;
    font-size: 1.25rem;
  }
  
  .loading, .empty {
    text-align: center;
    padding: 2rem;
    color: #888;
  }
</style>
