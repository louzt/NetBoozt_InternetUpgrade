/**
 * NetBoozt - Global Stores (Svelte Stores)
 * Estado global de la aplicación con Svelte stores
 * 
 * By LOUST (www.loust.pro)
 */

import { writable, derived, readable } from 'svelte/store';
import type { 
    NetworkAdapter, 
    DiagnosticResult, 
    TcpSettings, 
    NetworkMetrics,
    Alert,
    DNSHealth,
    FailoverEvent,
    SpeedTestResult
} from './types';

// ============================================
// Network State
// ============================================

export const adapters = writable<NetworkAdapter[]>([]);
export const selectedAdapter = writable<string>('');
export const diagnostic = writable<DiagnosticResult | null>(null);
export const tcpSettings = writable<TcpSettings | null>(null);

// ============================================
// Real-time Metrics
// ============================================

export interface MetricsSnapshot {
    timestamp: Date;
    downloadMbps: number;
    uploadMbps: number;
    latencyMs: number;
    packetsSent: number;
    packetsRecv: number;
    errors: number;
    drops: number;
}

// History buffer (last 5 minutes at 1s intervals = 300 points)
export const metricsHistory = writable<MetricsSnapshot[]>([]);
export const currentMetrics = writable<MetricsSnapshot | null>(null);

// Derived stats
export const averageMetrics = derived(metricsHistory, ($history) => {
    if ($history.length === 0) return null;
    
    const last60 = $history.slice(-60); // Last 60 seconds
    
    const avg = (arr: number[]) => arr.reduce((a, b) => a + b, 0) / arr.length;
    
    return {
        avgDownload: avg(last60.map(m => m.downloadMbps)),
        avgUpload: avg(last60.map(m => m.uploadMbps)),
        avgLatency: avg(last60.map(m => m.latencyMs)),
        peakDownload: Math.max(...last60.map(m => m.downloadMbps)),
        peakUpload: Math.max(...last60.map(m => m.uploadMbps)),
        totalErrors: last60.reduce((sum, m) => sum + m.errors, 0),
        totalDrops: last60.reduce((sum, m) => sum + m.drops, 0)
    };
});

// ============================================
// DNS State
// ============================================

export interface DNSProvider {
    id: string;
    name: string;
    primary: string;
    secondary: string;
    icon: string;
    tier: number;
    description: string;
    features: string[];
}

export const dnsProviders = readable<DNSProvider[]>([
    { 
        id: 'cloudflare', 
        name: 'Cloudflare', 
        primary: '1.1.1.1', 
        secondary: '1.0.0.1', 
        icon: '🌐',
        tier: 1,
        description: 'El DNS más rápido del mundo',
        features: ['Más rápido', 'Privacidad', 'Sin logs']
    },
    { 
        id: 'google', 
        name: 'Google', 
        primary: '8.8.8.8', 
        secondary: '8.8.4.4', 
        icon: '🔵',
        tier: 2,
        description: 'DNS público de Google',
        features: ['Confiable', 'Global', 'Anycast']
    },
    { 
        id: 'quad9', 
        name: 'Quad9', 
        primary: '9.9.9.9', 
        secondary: '149.112.112.112', 
        icon: '🛡️',
        tier: 3,
        description: 'DNS con bloqueo de malware',
        features: ['Seguridad', 'Sin malware', 'Privacidad']
    },
    { 
        id: 'opendns', 
        name: 'OpenDNS', 
        primary: '208.67.222.222', 
        secondary: '208.67.220.220', 
        icon: '🔶',
        tier: 4,
        description: 'DNS con filtrado de contenido',
        features: ['Filtrado', 'Control parental', 'Phishing block']
    },
    { 
        id: 'adguard', 
        name: 'AdGuard', 
        primary: '94.140.14.14', 
        secondary: '94.140.15.15', 
        icon: '🚫',
        tier: 5,
        description: 'DNS con bloqueo de anuncios',
        features: ['Ad-blocking', 'Trackers', 'Privacidad']
    },
    { 
        id: 'cleanbrowsing', 
        name: 'CleanBrowsing', 
        primary: '185.228.168.9', 
        secondary: '185.228.169.9', 
        icon: '👨‍👩‍👧',
        tier: 6,
        description: 'DNS familiar seguro',
        features: ['Familia', 'Seguro', 'Sin adultos']
    },
    { 
        id: 'dhcp', 
        name: 'Router/DHCP', 
        primary: 'auto', 
        secondary: 'auto', 
        icon: '🔄',
        tier: 7,
        description: 'DNS automático del ISP',
        features: ['Automático', 'ISP', 'Por defecto']
    }
]);

export const currentDNS = writable<string[]>([]);
export const dnsHealth = writable<Record<string, DNSHealth>>({});

// ============================================
// Auto-Failover State
// ============================================

export const autoFailoverEnabled = writable<boolean>(false);
export const currentTier = writable<number>(1);
export const failoverHistory = writable<FailoverEvent[]>([]);

// ============================================
// Alerts State
// ============================================

export const alerts = writable<Alert[]>([]);
export const activeAlerts = derived(alerts, ($alerts) => 
    $alerts.filter(a => !a.resolved)
);

export interface AlertThreshold {
    type: string;
    value: number;
    enabled: boolean;
    severity: 'info' | 'warning' | 'critical';
}

export const alertThresholds = writable<AlertThreshold[]>([
    { type: 'latency_high', value: 100, enabled: true, severity: 'warning' },
    { type: 'packet_loss', value: 2, enabled: true, severity: 'critical' },
    { type: 'speed_low', value: 10, enabled: true, severity: 'warning' },
    { type: 'dns_failure', value: 3, enabled: true, severity: 'critical' }
]);

// ============================================
// Speed Test State
// ============================================

export const speedTestRunning = writable<boolean>(false);
export const speedTestProgress = writable<number>(0);
export const speedTestResult = writable<SpeedTestResult | null>(null);
export const speedTestHistory = writable<SpeedTestResult[]>([]);

// ============================================
// Settings State
// ============================================

export interface AppSettings {
    theme: 'dark' | 'light' | 'system';
    language: 'es' | 'en';
    minimizeToTray: boolean;
    startWithWindows: boolean;
    showNotifications: boolean;
    monitoringInterval: number; // seconds
    autoFailover: boolean;
    soundAlerts: boolean;
}

const defaultSettings: AppSettings = {
    theme: 'dark',
    language: 'es',
    minimizeToTray: true,
    startWithWindows: false,
    showNotifications: true,
    monitoringInterval: 1,
    autoFailover: false,
    soundAlerts: true
};

function createSettingsStore() {
    const { subscribe, set, update } = writable<AppSettings>(defaultSettings);
    
    return {
        subscribe,
        set,
        update,
        reset: () => set(defaultSettings),
        load: (settings: Partial<AppSettings>) => update(s => ({ ...s, ...settings }))
    };
}

export const settings = createSettingsStore();

// ============================================
// UI State
// ============================================

export const loading = writable<boolean>(false);
export const error = writable<string | null>(null);
export const success = writable<string | null>(null);
export const activeTab = writable<string>('dashboard');

// Toast notifications
export interface Toast {
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
}

function createToastStore() {
    const { subscribe, update } = writable<Toast[]>([]);
    
    return {
        subscribe,
        add: (toast: Omit<Toast, 'id'>) => {
            const id = crypto.randomUUID();
            update(toasts => [...toasts, { ...toast, id }]);
            
            // Auto-remove after duration
            setTimeout(() => {
                update(toasts => toasts.filter(t => t.id !== id));
            }, toast.duration || 3000);
            
            return id;
        },
        remove: (id: string) => {
            update(toasts => toasts.filter(t => t.id !== id));
        },
        clear: () => update(() => [])
    };
}

export const toasts = createToastStore();

// ============================================
// Monitoring State
// ============================================

export const monitoringActive = writable<boolean>(false);
export const uptime = writable<number>(0); // seconds

// Update uptime every second when monitoring is active
let uptimeInterval: ReturnType<typeof setInterval> | null = null;

monitoringActive.subscribe(active => {
    if (active && !uptimeInterval) {
        uptimeInterval = setInterval(() => {
            uptime.update(n => n + 1);
        }, 1000);
    } else if (!active && uptimeInterval) {
        clearInterval(uptimeInterval);
        uptimeInterval = null;
        uptime.set(0);
    }
});

// Formatted uptime
export const formattedUptime = derived(uptime, ($uptime) => {
    const hours = Math.floor($uptime / 3600);
    const minutes = Math.floor(($uptime % 3600) / 60);
    const seconds = $uptime % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
});
