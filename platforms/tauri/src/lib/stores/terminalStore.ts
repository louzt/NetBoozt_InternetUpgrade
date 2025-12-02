/**
 * Terminal Log Store
 * Store centralizado para logs que se muestran en la terminal
 * By LOUST
 */

import { writable, derived } from 'svelte/store';

export interface LogEntry {
    id: string;
    timestamp: Date;
    level: 'info' | 'warn' | 'error' | 'debug' | 'dryrun';
    message: string;
    source?: string;
}

function createTerminalStore() {
    const { subscribe, set, update } = writable<LogEntry[]>([]);
    
    const MAX_LOGS = 500;
    
    function addLog(level: LogEntry['level'], message: string, source?: string) {
        const entry: LogEntry = {
            id: crypto.randomUUID(),
            timestamp: new Date(),
            level,
            message,
            source
        };
        
        update(logs => [...logs.slice(-(MAX_LOGS - 1)), entry]);
        return entry;
    }
    
    return {
        subscribe,
        
        info: (message: string, source?: string) => addLog('info', message, source),
        warn: (message: string, source?: string) => addLog('warn', message, source),
        error: (message: string, source?: string) => addLog('error', message, source),
        debug: (message: string, source?: string) => addLog('debug', message, source),
        dryrun: (message: string, source?: string) => addLog('dryrun', message, source),
        
        // Para agregar logs desde eventos del backend
        addFromEvent: (event: { level: string; message: string }) => {
            addLog(event.level as LogEntry['level'], event.message);
        },
        
        clear: () => {
            set([]);
            addLog('info', 'Terminal limpiada');
        },
        
        // Agregar múltiples logs de dry-run de una vez
        addDryRunBatch: (commands: string[]) => {
            const timestamp = new Date();
            const entries: LogEntry[] = commands.map((cmd, i) => ({
                id: `dryrun-${timestamp.getTime()}-${i}`,
                timestamp,
                level: 'dryrun' as const,
                message: cmd,
                source: 'dry-run'
            }));
            
            update(logs => [...logs.slice(-(MAX_LOGS - entries.length)), ...entries]);
        }
    };
}

export const terminalLogs = createTerminalStore();

// Derived store para solo logs de dry-run
export const dryRunLogs = derived(terminalLogs, $logs => 
    $logs.filter(l => l.level === 'dryrun')
);

// Derived store para solo errores
export const errorLogs = derived(terminalLogs, $logs => 
    $logs.filter(l => l.level === 'error')
);
