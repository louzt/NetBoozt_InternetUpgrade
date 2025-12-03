/**
 * NetBoozt - TypeScript Types
 * Definiciones de tipos para la aplicación
 * 
 * By LOUST (www.loust.pro)
 */

// ============================================
// Network Types
// ============================================

export interface NetworkAdapter {
    name: string;
    description: string;
    status: string;
    link_speed: string;
    mac_address: string;
    ipv4_address?: string;
    ipv6_address?: string;
    gateway?: string;
    dns_servers?: string[];
}

export interface TcpSettings {
    autotuning: string;
    rss: string;
    rsc: string;
    ecn: string;
    timestamps: string;
    chimney: string;
    congestion_provider?: string;
    // Campos adicionales para optimizaciones avanzadas
    fast_open?: string;
    hystart?: string;
    prr?: string;
    pacing?: string;
    initial_rto?: string;
    rack?: string;
}

// ============================================
// Diagnostic Types
// ============================================

export type NetworkHealth = 'Excellent' | 'Good' | 'Fair' | 'Poor' | 'Bad' | 'Down';
export type FailurePoint = 'None' | 'Adapter' | 'Router' | 'Isp' | 'Dns' | 'Internet';

export interface DiagnosticResult {
    health: NetworkHealth;
    score: number;
    failure_point: FailurePoint;
    adapter_ok: boolean;
    adapter_name: string;
    router_ok: boolean;
    router_latency_ms: number;
    isp_ok: boolean;
    isp_latency_ms: number;
    dns_ok: boolean;
    dns_latency_ms: number;
    internet_ok: boolean;
    internet_latency_ms: number;
    recommendation: string;
}

// ============================================
// Metrics Types
// ============================================

export interface NetworkMetrics {
    timestamp: string;
    download_mbps: number;
    upload_mbps: number;
    latency_ms: number;
    packets_sent: number;
    packets_recv: number;
    packets_sent_per_sec: number;
    packets_recv_per_sec: number;
    errors_in: number;
    errors_out: number;
    drops_in: number;
    drops_out: number;
}

export interface MetricsSummary {
    avg_download_mbps: number;
    avg_upload_mbps: number;
    peak_download_mbps: number;
    peak_upload_mbps: number;
    avg_latency_ms: number;
    total_errors: number;
    total_drops: number;
    uptime_seconds: number;
}

// ============================================
// DNS Types
// ============================================

export type DNSStatus = 'up' | 'slow' | 'down' | 'unknown';

export interface DNSHealth {
    server: string;
    status: DNSStatus;
    latency_ms: number;
    last_check: string;
    consecutive_failures: number;
    success_rate: number;
}

export interface DNSConfig {
    adapter: string;
    servers: string[];
    is_dhcp: boolean;
}

// ============================================
// Alert Types
// ============================================

export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertType = 
    | 'latency_high' 
    | 'packet_loss_high' 
    | 'speed_low' 
    | 'dns_failure' 
    | 'adapter_error'
    | 'failover_triggered';

export interface Alert {
    id: string;
    type: AlertType;
    severity: AlertSeverity;
    message: string;
    timestamp: string;
    current_value?: number;
    threshold_value?: number;
    resolved: boolean;
    resolved_at?: string;
}

// ============================================
// Failover Types
// ============================================

export interface FailoverEvent {
    timestamp: string;
    from_tier: number;
    to_tier: number;
    from_dns: string;
    to_dns: string;
    reason: string;
    success: boolean;
}

export interface FailoverStats {
    total_failovers: number;
    successful: number;
    failed: number;
    last_failover?: string;
    enabled: boolean;
}

// ============================================
// Speed Test Types
// ============================================

export interface SpeedTestResult {
    id: string;
    timestamp: string;
    download_mbps: number;
    upload_mbps: number;
    ping_ms: number;
    jitter_ms: number;
    server_name: string;
    server_location: string;
    isp: string;
}

export interface SpeedTestProgress {
    stage: 'idle' | 'ping' | 'download' | 'upload' | 'complete';
    progress: number; // 0-100
    current_speed?: number;
}

// ============================================
// Optimization Types
// ============================================

export type OptimizationProfile = 'Conservative' | 'Balanced' | 'Aggressive';

export interface Optimization {
    id: string;
    name: string;
    description: string;
    category: string;
    risk_level: 'low' | 'medium' | 'high';
    enabled: boolean;
    command?: string;
    registry_key?: string;
}

export interface OptimizationResult {
    profile: OptimizationProfile;
    applied: string[];
    failed: string[];
    requires_restart: boolean;
}

// ============================================
// Settings Types
// ============================================

export interface AppConfig {
    theme: 'dark' | 'light' | 'system';
    language: 'es' | 'en';
    minimize_to_tray: boolean;
    start_with_windows: boolean;
    show_notifications: boolean;
    monitoring_interval_ms: number;
    auto_failover_enabled: boolean;
    sound_alerts: boolean;
    alert_thresholds: Record<AlertType, number>;
}

// ============================================
// Event Types (for Tauri events)
// ============================================

export interface TauriEvent<T> {
    event: string;
    payload: T;
}

export interface MetricsUpdateEvent {
    metrics: NetworkMetrics;
}

export interface AlertTriggeredEvent {
    alert: Alert;
}

export interface FailoverTriggeredEvent {
    event: FailoverEvent;
}

export interface DNSHealthUpdateEvent {
    health: Record<string, DNSHealth>;
}
